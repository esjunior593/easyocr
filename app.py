from flask import Flask, request, jsonify
import easyocr
import numpy as np
from PIL import Image
import io

app = Flask(__name__)

# Inicializa el lector de EasyOCR (soporta múltiples idiomas)
reader = easyocr.Reader(['en', 'es'])  # Inglés y español

@app.route('/ocr', methods=['POST'])
def ocr():
    # Verifica si se envió una imagen
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    # Lee la imagen
    image_file = request.files['image']
    image = Image.open(image_file).convert('RGB')  # Convierte a RGB
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