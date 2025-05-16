from flask import Flask, render_template, request, jsonify
import tensorflow as tf
import numpy as np
from PIL import Image
import pickle
import io
import os
import matplotlib.pyplot as plt
import logging
import socket

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

MODEL_PATH = "D:\\CODEVERSE\\DNACreator\\skin_lesion_model.h5"
HISTORY_PATH = "D:\\CODEVERSE\\DNACreator\\training_history.pkl"

# Load model
try:
    logger.info("Loading model from %s", MODEL_PATH)
    model = tf.keras.models.load_model(MODEL_PATH)
except Exception as e:
    logger.error("Failed to load model: %s", str(e))
    raise

# Load training history for plotting
if os.path.exists(HISTORY_PATH):
    try:
        with open(HISTORY_PATH, "rb") as f:
            history_dict = pickle.load(f)
        logger.info("Loaded training history from %s", HISTORY_PATH)
    except Exception as e:
        logger.error("Failed to load training history: %s", str(e))
        history_dict = {}
else:
    logger.warning("Training history file %s not found", HISTORY_PATH)
    history_dict = {}

# Plot accuracy history
if "accuracy" in history_dict and "val_accuracy" in history_dict:
    try:
        plt.plot(history_dict['accuracy'], label='Train Accuracy')
        plt.plot(history_dict['val_accuracy'], label='Val Accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.title('Training History')
        plt.legend()
        plt.grid(True)
        plt.savefig("static/training_plot.png")
        plt.close()
        logger.info("Generated training history plot at static/training_plot.png")
    except Exception as e:
        logger.error("Failed to generate training plot: %s", str(e))

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

if __name__ == "__main__":
    ports = [3000, 3001, 3002]  # Try these ports
    for port in ports:
        try:
            logger.info("Attempting to start Flask application on port %d", port)
            app.run(debug=True, port=port)
            break
        except socket.error as e:
            logger.error("Port %d failed: %s", port, str(e))
            if port == ports[-1]:
                logger.error("All ports failed. Please free a port or check permissions.")
                raise