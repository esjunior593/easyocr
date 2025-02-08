from flask import Flask, request, jsonify
import easyocr
import requests
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# Inicializar el OCR una sola vez para optimizar rendimiento
reader = easyocr.Reader(['es'])

@app.route('/ocr', methods=['POST'])
def ocr():
    data = request.get_json()

    if not data or 'image_url' not in data:
        return jsonify({"error": "Falta la URL de la imagen"}), 400

    image_url = data['image_url']

    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Asegura que la imagen fue descargada correctamente

        img = Image.open(BytesIO(response.content)).convert('RGB')  # Convertir a RGB
        result = reader.readtext(img, detail=0)  # Solo extraer el texto

        return jsonify({"text": " ".join(result)})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"No se pudo descargar la imagen: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Error en el procesamiento de OCR: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
