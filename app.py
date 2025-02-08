import cv2
import numpy as np
import requests
import easyocr
from skimage.metrics import structural_similarity as ssim
from flask import Flask, request, jsonify

app = Flask(__name__)
reader = easyocr.Reader(['es'])  # Cargar EasyOCR en español

def download_image(url):
    """Descargar imagen desde URL con User-Agent y convertirla a formato OpenCV."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    except requests.exceptions.RequestException:
        return None

def verificar_autenticidad(image_url):
    """Verifica si la imagen fue editada usando SSIM."""
    imagen = download_image(image_url)
    if imagen is None:
        return {"error": "No se pudo descargar la imagen."}

    # Convertir a escala de grises
    imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    # Simular comparación con sí misma para prueba (esto debería ser una imagen original almacenada)
    similitud = ssim(imagen_gris, imagen_gris)  # 👈 Este código debe cambiar en producción

    # Si el SSIM es menor a 0.97, se considera posible fraude
    if similitud < 0.97:
        return {"resultado": "❌ Comprobante editado detectado.", "ssim": round(similitud, 4)}
    return None  # Si es original, sigue con el OCR

@app.route('/ocr', methods=['POST'])
def procesar_ocr():
    """Extrae texto de una imagen, pero primero verifica si es falsa."""
    data = request.json
    image_url = data.get("image_url")

    if not image_url:
        return jsonify({"error": "❌ Falta la URL de la imagen"}), 400

    # 🔎 **1️⃣ Verificar si la imagen es falsa antes de extraer el texto**
    fraude = verificar_autenticidad(image_url)
    if fraude:
        return jsonify(fraude)  # 🚫 Si es fraudulento, se detiene aquí.

    # 🔍 **2️⃣ Si la imagen es original, extraer texto con OCR**
    imagen = download_image(image_url)
    if imagen is None:
        return jsonify({"error": "❌ No se pudo descargar la imagen para OCR."}), 400

    resultado = reader.readtext(imagen)

    # Convertir salida de EasyOCR en un solo texto
    texto_extraido = " ".join([res[1] for res in resultado])

    return jsonify({"texto": texto_extraido})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
