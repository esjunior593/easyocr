import cv2
import numpy as np
import requests
from skimage.metrics import structural_similarity as ssim
from flask import Flask, request, jsonify

app = Flask(__name__)

def download_image(url):
    """Descargar imagen desde URL y convertirla a formato OpenCV."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    except requests.exceptions.RequestException as e:
        return None

def compare_images(original_url, edited_url):
    """Comparar la similitud estructural (SSIM) entre dos imágenes."""
    original = download_image(original_url)
    edited = download_image(edited_url)

    if original is None or edited is None:
        return {"error": "No se pudieron descargar ambas imágenes correctamente."}

    # Redimensionar la imagen editada al tamaño de la original para comparar correctamente
    edited = cv2.resize(edited, (original.shape[1], original.shape[0]))

    # Convertir a escala de grises para una mejor comparación
    original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    edited_gray = cv2.cvtColor(edited, cv2.COLOR_BGR2GRAY)

    # Calcular el SSIM (Structural Similarity Index)
    similarity = ssim(original_gray, edited_gray)

    # Determinar si es fraude o no
    if similarity < 0.97:
        return {"resultado": "❌ Edición confirmada (posible fraude)", "ssim": round(similarity, 4)}
    else:
        return {"resultado": "✅ Imagen original (sin ediciones)", "ssim": round(similarity, 4)}

@app.route('/verificar', methods=['POST'])
def verificar_comprobante():
    """API para verificar si un comprobante ha sido editado."""
    data = request.json
    original_url = data.get("original_url")
    edited_url = data.get("edited_url")

    if not original_url or not edited_url:
        return jsonify({"error": "Faltan las URLs de las imágenes."}), 400

    resultado = compare_images(original_url, edited_url)
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
