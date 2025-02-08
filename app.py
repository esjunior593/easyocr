import easyocr
import requests
import cv2
import numpy as np
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# 🔹 Función para descargar la imagen desde una URL
def descargar_imagen(image_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}  # Evitar bloqueos por política de User-Agent
        response = requests.get(image_url, headers=headers, stream=True)
        response.raise_for_status()

        image_path = "temp.jpg"
        with open(image_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        return image_path
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error al descargar la imagen: {str(e)}")

# 🔹 Función para analizar ediciones con ELA (Error Level Analysis)
def analizar_ela(ruta_imagen):
    try:
        # Cargar la imagen original
        imagen = cv2.imread(ruta_imagen)

        # Guardar la imagen con menor calidad para detectar diferencias
        cv2.imwrite("temp_recomp.jpg", imagen, [cv2.IMWRITE_JPEG_QUALITY, 90])
        imagen_recomp = cv2.imread("temp_recomp.jpg")

        # Comparar la imagen original con la recomprimida
        ela = cv2.absdiff(imagen, imagen_recomp)
        _, resultado = cv2.threshold(ela, 15, 255, cv2.THRESH_BINARY)

        # Calcular el porcentaje de píxeles modificados
        porcentaje_editado = np.sum(resultado) / np.prod(resultado.shape) * 100

        os.remove("temp_recomp.jpg")  # Eliminar imagen temporal

        if porcentaje_editado > 10:  # 🔹 Umbral de edición (ajustable)
            return "❌ Posible edición detectada en el comprobante."
        return "✅ No se detectaron ediciones."
    except Exception as e:
        return f"⚠️ Error en la validación de edición: {str(e)}"

# 🔹 Función para procesar la imagen con EasyOCR
def procesar_ocr(ruta_imagen):
    reader = easyocr.Reader(["es"])  # Cargar modelo en español
    text = reader.readtext(ruta_imagen, detail=0)
    return " ".join(text)

# 🔹 Endpoint para recibir imágenes y procesarlas con validación de edición
@app.route('/ocr', methods=['POST'])
def ocr():
    data = request.get_json()
    image_url = data.get("imageUrl")

    if not image_url:
        return jsonify({"error": "❌ Falta la URL de la imagen"}), 400

    try:
        # 1️⃣ Descargar la imagen
        image_path = descargar_imagen(image_url)

        # 2️⃣ Verificar si la imagen fue editada con ELA
        resultado_ela = analizar_ela(image_path)
        print(resultado_ela)

        # 3️⃣ Si detecta edición, rechazar el comprobante
        if "❌" in resultado_ela:
            os.remove(image_path)  # Eliminar imagen descargada
            return jsonify({
                "error": "🚨 Comprobante sospechoso de haber sido editado.",
                "detalle": resultado_ela
            }), 400

        # 4️⃣ Si no fue editado, procesar con EasyOCR
        texto_extraido = procesar_ocr(image_path)
        os.remove(image_path)  # Eliminar imagen después del procesamiento

        return jsonify({"texto": texto_extraido, "validacion": resultado_ela})

    except Exception as e:
        return jsonify({"error": f"⚠️ Error en el procesamiento de OCR: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
