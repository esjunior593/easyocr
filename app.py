from flask import Flask, request, jsonify
import easyocr
import os

app = Flask(__name__)

# Cargar EasyOCR
reader = easyocr.Reader(['es'])  # Puedes cambiar el idioma si es necesario

@app.route('/ocr', methods=['POST'])
def process_ocr():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No se recibió ninguna imagen"}), 400

        image = request.files['image']
        image_path = "temp_image.jpg"
        image.save(image_path)

        # Procesar OCR
        result = reader.readtext(image_path, detail=0)
        os.remove(image_path)  # Eliminar la imagen después del OCR

        return jsonify({"text": " ".join(result)})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    from server import app
    app.run(host="0.0.0.0", port=8080)

