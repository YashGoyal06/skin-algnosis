from flask import Flask, render_template, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# URL to download the model from Google Drive
MODEL_URL = "https://drive.google.com/uc?export=download&id=1uYA2Ik96PX_dbSOl4Sm_4uLLJr08SFlz"
MODEL_PATH = "/tmp/skin_lesion_model.h5"

# Download the model if it doesn't exist
if not os.path.exists(MODEL_PATH):
    logger.info("Downloading model from %s", MODEL_URL)
    try:
        response = requests.get(MODEL_URL, stream=True)
        response.raise_for_status()
        with open(MODEL_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.info("Model downloaded successfully to %s", MODEL_PATH)
    except Exception as e:
        logger.error("Failed to download model: %s", str(e))
        raise

# Load model
try:
    logger.info("Loading model from %s", MODEL_PATH)
    model = tf.keras.models.load_model(MODEL_PATH)
except Exception as e:
    logger.error("Failed to load model: %s", str(e))
    raise

IMG_SIZE = (224, 224)
CONFIDENCE_THRESHOLD = 0.30

label_map = {
    0: "Melanoma",
    1: "Melanocytic nevus",
    2: "Basal cell carcinoma",
    3: "Actinic keratosis",
    4: "Benign keratosis",
    5: "Dermatofibroma",
    6: "Vascular lesion",
    7: "Squamous cell carcinoma"
}

def preprocess_image(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image = image.resize(IMG_SIZE)
        image_array = tf.keras.utils.img_to_array(image)
        image_array = np.expand_dims(image_array, axis=0)
        return image_array / 255.0
    except Exception as e:
        logger.error("Failed to preprocess image: %s", str(e))
        raise

@app.route("/templates/form.html", methods=["GET"])
def form():
    logger.info("Serving form page at /templates/form.html")
    return render_template("form.html", history_plot="/static/training_plot.png")

@app.route("/predict", methods=["POST"])
def predict():
    logger.info("Received prediction request")
    if "image" not in request.files:
        logger.warning("No image uploaded in request")
        return jsonify({"error": "No image uploaded"}), 400

    try:
        image = request.files["image"].read()
        img_array = preprocess_image(image)

        logger.info("Running model prediction")
        prediction = model.predict(img_array)[0]
        predicted_index = int(np.argmax(prediction))
        confidence = float(prediction[predicted_index])

        if confidence < CONFIDENCE_THRESHOLD:
            result = {
                "prediction": "Low confidence",
                "confidence": f"{confidence * 100:.2f}%",
                "message": "⚠ This image is not confidently recognized. Please upload a clearer image."
            }
            logger.info("Prediction: Low confidence (%.2f%%)", confidence * 100)
        else:
            result = {
                "prediction": label_map.get(predicted_index, "Unknown"),
                "confidence": f"{confidence * 100:.2f}%"
            }
            logger.info("Prediction: %s (Confidence: %.2f%%)", result["prediction"], confidence * 100)

        return jsonify(result), 200
    except Exception as e:
        logger.error("Error processing image: %s", str(e))
        return jsonify({"error": f"Error processing image: {str(e)}"}), 500

# Vercel serverless function handler
def handler(event, context):
    from serverless_wsgi import handle_request
    return handle_request(app, event, context)
