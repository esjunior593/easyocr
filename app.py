from flask import Flask, request, jsonify
import easyocr
import requests
import os

app = Flask(__name__)

# Inicializar el lector de EasyOCR con español
reader = easyocr.Reader(['es'])  

def descargar_imagen(image_url):
    """Descarga una imagen desde una URL y la guarda temporalmente."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(image_url, headers=headers, stream=True)
        response.raise_for_status()  # Verifica errores en la descarga
        
        image_path = "temp.jpg"
        with open(image_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        return image_path

    except requests.exceptions.RequestException as e:
        return {"error": f"No se pudo descargar la imagen: {e}"}


def procesar_ocr(image_url):
    """Procesa la imagen con EasyOCR y devuelve el texto detectado."""
    image_path = descargar_imagen(image_url)

    # Si hay un error en la descarga, devolverlo
    if isinstance(image_path, dict):
        return image_path  

    try:
        # Procesar la imagen con EasyOCR
        resultado = reader.readtext(image_path, detail=0)  # detail=0 devuelve solo el texto

        os.remove(image_path)  # Eliminar la imagen temporal después del OCR

        return {"text": " ".join(resultado)}

    except Exception as e:
        return {"error": f"Error en el procesamiento de OCR: {str(e)}"}


@app.route('/ocr', methods=['POST'])
def ocr():
    """Endpoint para recibir una URL y procesar OCR."""
    data = request.json

    if not data or "image_url" not in data:
        return jsonify({"error": "Falta la URL de la imagen"}), 400

    resultado_ocr = procesar_ocr(data["image_url"])
    return jsonify(resultado_ocr)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
