from flask import Flask, request, jsonify
import easyocr
import requests
from io import BytesIO

app = Flask(__name__)
reader = easyocr.Reader(["es", "en"])  # Idiomas: Español e Inglés

@app.route("/ocr", methods=["POST"])
def ocr():
    data = request.json
    image_url = data.get("imageUrl")  # Recibir la URL de la imagen

    if not image_url:
        return jsonify({"error": "Falta la URL de la imagen"}), 400

    try:
        # Descargar la imagen desde la URL
        response = requests.get(image_url)
        if response.status_code != 200:
            return jsonify({"error": "No se pudo descargar la imagen"}), 400

        img = BytesIO(response.content)  # Convertir en objeto de imagen

        # Procesar la imagen con EasyOCR
        result = reader.readtext(img, detail=0)
        text = " ".join(result)  # Convertir la lista de texto en un solo string

        return jsonify({"text": text})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
