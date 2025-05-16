import matplotlib.pyplot as plt
import pickle
import os

HISTORY_PATH = "training_history.pkl"

# Load training history
if os.path.exists(HISTORY_PATH):
    try:
        with open(HISTORY_PATH, "rb") as f:
            history_dict = pickle.load(f)
        print("Loaded training history from", HISTORY_PATH)
    except Exception as e:
        print("Failed to load training history:", str(e))
        history_dict = {}
else:
    print("Training history file not found:", HISTORY_PATH)
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
        print("Generated training history plot at static/training_plot.png")
    except Exception as e:
        print("Failed to generate training plot:", str(e))