from flask import Flask, request, jsonify
import easyocr
import numpy as np
from PIL import Image
import requests
from io import BytesIO

app = Flask(__name__)

# Inicializa el lector de EasyOCR (soporta múltiples idiomas)
reader = easyocr.Reader(['en', 'es'])  # Inglés y español

@app.route('/ocr', methods=['POST'])
def ocr():
    # Verifica si se envió una URL
    if 'url' not in request.json:
        return jsonify({"error": "No URL provided"}), 400

    # Obtén la URL de la imagen
    image_url = request.json['url']

    # Descarga la imagen desde la URL
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Lanza un error si la descarga falla
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to download image: {str(e)}"}), 400

    # Convierte la imagen a un formato que EasyOCR pueda procesar
    image = Image.open(BytesIO(response.content)).convert('RGB')
    image_np = np.array(image)  # Convierte a un array de NumPy

    # Procesa la imagen con EasyOCR
    results = reader.readtext(image_np)

    # Formatea los resultados
    output = []
    for (bbox, text, confidence) in results:
        output.append({
            "text": text,
            "confidence": float(confidence),
            "bounding_box": bbox
        })

    return jsonify(output)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)