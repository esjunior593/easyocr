import cv2
import numpy as np
import requests
import easyocr
from skimage.metrics import structural_similarity as ssim
from flask import Flask, request, jsonify

app = Flask(__name__)
reader = easyocr.Reader(['es'])  # Inicializar EasyOCR en español

def download_image(url):
    """Descargar imagen desde URL y convertirla a formato OpenCV."""
    try:
        print(f"📥 Descargando imagen desde: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None:
            print(f"🚨 No se pudo decodificar la imagen: {url}")
        return image
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al descargar imagen: {e}")
        return None

def extract_text(image_url):
    """Realizar OCR en la imagen descargada desde una URL."""
    image = download_image(image_url)
    if image is None:
        return {"error": "❌ No se pudo descargar la imagen."}
    
    # Convertir la imagen a escala de grises (opcional para mejorar OCR)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Extraer texto con EasyOCR
    result = reader.readtext(gray_image, detail=0)
    extracted_text = " ".join(result)
    
    print("📄 Texto extraído:", extracted_text)
    
    return {"text": extracted_text}

def compare_images(original_url, edited_url):
    """Comparar la similitud estructural (SSIM) entre dos imágenes."""
    original = download_image(original_url)
    edited = download_image(edited_url)

    if original is None or edited is None:
        return {"error": "❌ No se pudieron descargar ambas imágenes correctamente."}

    # Redimensionar la imagen editada al tamaño de la original
    edited = cv2.resize(edited, (original.shape[1], original.shape[0]))

    # Convertir a escala de grises
    original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    edited_gray = cv2.cvtColor(edited, cv2.COLOR_BGR2GRAY)

    # Calcular SSIM
    similarity = ssim(original_gray, edited_gray)
    similarity_rounded = round(similarity, 4)

    if similarity < 0.97:
        print(f"🚨 Posible fraude detectado - SSIM: {similarity_rounded}")
        return {"resultado": "❌ Edición confirmada (posible fraude)", "ssim": similarity_rounded}
    else:
        print(f"✅ Imagen original detectada - SSIM: {similarity_rounded}")
        return {"resultado": "✅ Imagen original (sin ediciones)", "ssim": similarity_rounded}

@app.route('/ocr', methods=['POST'])
def ocr():
    """API para extraer texto de una imagen."""
    data = request.json
    image_url = data.get("image_url")

    if not image_url:
        return jsonify({"error": "❌ Falta la URL de la imagen"}), 400

    return jsonify(extract_text(image_url))

@app.route('/verificar', methods=['POST'])
def verificar_comprobante():
    """API para verificar si un comprobante ha sido editado."""
    data = request.json
    original_url = data.get("original_url")
    edited_url = data.get("edited_url")

    if not original_url or not edited_url:
        return jsonify({"error": "❌ Faltan las URLs de las imágenes."}), 400

    return jsonify(compare_images(original_url, edited_url))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
