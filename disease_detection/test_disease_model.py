
import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "rice_disease_model.keras"
CLASS_PATH = BASE_DIR / "rice_disease_classes.json"
IMAGE_PATH = BASE_DIR / "uploads" / "rice_leaf.jpg"

# Check required files
for path in [MODEL_PATH, CLASS_PATH, IMAGE_PATH]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

# Load model and class names
model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASS_PATH, "r", encoding="utf-8") as f:
    class_names = json.load(f)

# Prepare the leaf image
image = Image.open(IMAGE_PATH).convert("RGB")
image = image.resize((128, 128))

image_array = np.array(image, dtype=np.float32)
image_array = np.expand_dims(image_array, axis=0)

# Predict disease
predictions = model.predict(image_array, verbose=0)[0]
best_index = int(np.argmax(predictions))

print("\n--- Rice Leaf Disease Prediction ---")
print("Predicted class:", class_names[best_index])
print("Model confidence:", round(float(predictions[best_index]) * 100, 2), "%")
print("\nNote: This is an initial test, not a verified diagnosis.")
