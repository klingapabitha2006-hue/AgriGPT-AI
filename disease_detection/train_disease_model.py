
import json
from pathlib import Path

import tensorflow as tf
from tensorflow.keras import layers, models

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset" / "rice_leaf_diseases"
MODEL_PATH = BASE_DIR / "rice_disease_model.keras"
CLASS_PATH = BASE_DIR / "rice_disease_classes.json"

# Lightweight settings for an 8 GB RAM laptop
IMAGE_SIZE = (128, 128)
BATCH_SIZE = 8
EPOCHS = 15
SEED = 42

tf.keras.utils.set_random_seed(SEED)

# Check dataset
if not DATASET_DIR.exists():
    raise FileNotFoundError(
        f"Dataset folder not found: {DATASET_DIR}"
    )

class_folders = sorted(
    p.name for p in DATASET_DIR.iterdir() if p.is_dir()
)

if len(class_folders) != 3:
    raise ValueError(
        f"Expected 3 disease folders, found: {class_folders}"
    )

print("Disease classes:", class_folders)

# Load images and split into training and validation
train_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR,
    validation_split=0.2,
    subset="training",
    seed=SEED,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="int",
    shuffle=True
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR,
    validation_split=0.2,
    subset="validation",
    seed=SEED,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="int",
    shuffle=True
)

class_names = train_ds.class_names
print("Model class order:", class_names)

# Save class names for later predictions
with open(CLASS_PATH, "w", encoding="utf-8") as f:
    json.dump(class_names, f, indent=2)

# Small CNN model
data_augmentation = models.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.08),
    layers.RandomZoom(0.1),
])

model = models.Sequential([
    layers.Input(shape=(128, 128, 3)),
    data_augmentation,
    layers.Rescaling(1.0 / 255),

    layers.Conv2D(16, 3, padding="same", activation="relu"),
    layers.MaxPooling2D(),

    layers.Conv2D(32, 3, padding="same", activation="relu"),
    layers.MaxPooling2D(),

    layers.Conv2D(64, 3, padding="same", activation="relu"),
    layers.MaxPooling2D(),

    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.3),
    layers.Dense(32, activation="relu"),
    layers.Dense(len(class_names), activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

callbacks = [
    tf.keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=4,
        restore_best_weights=True
    )
]

# Train the model
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    callbacks=callbacks
)

# Save trained model
model.save(MODEL_PATH)

print("\nTraining completed!")
print("Model saved to:", MODEL_PATH)
print("Class names saved to:", CLASS_PATH)
print("Final training accuracy:",
      round(history.history["accuracy"][-1] * 100, 2), "%")
print("Final validation accuracy:",
      round(history.history["val_accuracy"][-1] * 100, 2), "%")
print("Note: Validation accuracy is only an initial estimate.")
