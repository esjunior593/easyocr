import flask
import requests
import easyocr
import numpy as np
import cv2
import io
from PIL import Image

app = flask.Flask(__name__)

# Inicializar OCR
reader = easyocr.Reader(['es'])

def analizar_ela(imagen_url):
    try:
        # Descargar imagen desde URL
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(imagen_url, headers=headers)
        response.raise_for_status()

        # Convertir la imagen a formato PIL
        imagen = Image.open(io.BytesIO(response.content)).convert('RGB')

        # Guardar versión comprimida
        imagen_comprimida = io.BytesIO()
        imagen.save(imagen_comprimida, format='JPEG', quality=85)
        imagen_comprimida = Image.open(imagen_comprimida)

        # Convertir ambas imágenes a matrices NumPy
        original = np.array(imagen, dtype=np.float32)
        comprimida = np.array(imagen_comprimida, dtype=np.float32)

        # Calcular el Error Level Analysis (ELA)
        diferencia = np.abs(original - comprimida)
        intensidad_ela = np.mean(diferencia)

        print(f"📊 Intensidad de ELA detectada: {intensidad_ela}")

        # Si la diferencia es alta, indicar que la imagen fue editada
        if intensidad_ela > 10:  # Puedes ajustar este umbral
            return {"editado": True, "nivel": intensidad_ela}

        return {"editado": False, "nivel": intensidad_ela}

    except Exception as e:
        return {"error": f"Error en ELA: {str(e)}"}

@app.route('/ocr', methods=['POST'])
def procesar_ocr():
    data = flask.request.get_json()
    
    if not data or 'image_url' not in data:
        return flask.jsonify({"error": "❌ Falta la URL de la imagen"}), 400

    imagen_url = data['image_url']

    # 🔎 **Verificar si la imagen ha sido editada con ELA**
    resultado_ela = analizar_ela(imagen_url)
    
    if resultado_ela.get("editado"):
        return flask.jsonify({
            "error": "🚨 Comprobante sospechoso de haber sido editado.",
            "detalle": f"❌ Posible edición detectada en el comprobante (Nivel de ELA: {resultado_ela['nivel']:.2f})."
        }), 400

    try:
        # **Descargar la imagen**
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(imagen_url, headers=headers)
        response.raise_for_status()
        
        # Convertir la imagen en formato compatible con EasyOCR
        image_bytes = io.BytesIO(response.content)

        # **Extraer texto con EasyOCR**
        text_result = reader.readtext(np.array(Image.open(image_bytes)), detail=0)

        return flask.jsonify({"text": " ".join(text_result)})

    except Exception as e:
        return flask.jsonify({"error": f"Error en el procesamiento de OCR: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
