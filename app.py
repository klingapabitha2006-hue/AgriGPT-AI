

import os
import sys
import shutil

import math

import inspect

import re



from flask import Flask, jsonify, request

from flask_cors import CORS

from knowledge import search_knowledge, detect_response_language, tamil_to_tanglish

from crop_recommendation import recommend_crop

import joblib

from deep_translator import GoogleTranslator

# Added for rice leaf disease detection only
import json
import numpy as np
import tensorflow as tf
from PIL import Image, UnidentifiedImageError





# ---------------------------------------

# FLASK APPLICATION

# ---------------------------------------



app = Flask(__name__)

CORS(app)





# ---------------------------------------

# BASE DIRECTORY AND ML MODEL

# ---------------------------------------



BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "crop_model.pkl")



crop_model = joblib.load(MODEL_PATH)


# ---------------------------------------
# RICE LEAF DISEASE MODEL (ADDED)
# ---------------------------------------

DISEASE_DIR = os.path.join(BASE_DIR, "disease_detection")
DISEASE_DATASET_DIR = os.path.join(
    DISEASE_DIR, "dataset", "rice_leaf_diseases"
)

# Keep the original trained model as a safe fallback.
ORIGINAL_DISEASE_MODEL_PATH = os.path.join(
    DISEASE_DIR, "rice_disease_model.keras"
)
ORIGINAL_DISEASE_CLASS_PATH = os.path.join(
    DISEASE_DIR, "rice_disease_classes.json"
)

# The training mode creates these files. If they exist, the app uses the
# improved candidate; otherwise it continues using the original model.
IMPROVED_DISEASE_MODEL_PATH = os.path.join(
    DISEASE_DIR, "rice_disease_model_improved.keras"
)
IMPROVED_DISEASE_CLASS_PATH = os.path.join(
    DISEASE_DIR, "rice_disease_classes_improved.json"
)

if (
    os.path.isfile(IMPROVED_DISEASE_MODEL_PATH)
    and os.path.isfile(IMPROVED_DISEASE_CLASS_PATH)
):
    DISEASE_MODEL_PATH = IMPROVED_DISEASE_MODEL_PATH
    DISEASE_CLASS_PATH = IMPROVED_DISEASE_CLASS_PATH
    print("Loading improved rice disease model...")
else:
    DISEASE_MODEL_PATH = ORIGINAL_DISEASE_MODEL_PATH
    DISEASE_CLASS_PATH = ORIGINAL_DISEASE_CLASS_PATH
    print("Loading original rice disease model...")

disease_model = tf.keras.models.load_model(DISEASE_MODEL_PATH)

with open(DISEASE_CLASS_PATH, "r", encoding="utf-8") as file:
    disease_class_names = json.load(file)





# ---------------------------------------

# LANGUAGE HELPER FUNCTIONS

# ---------------------------------------



def contains_tamil(text):

    if not text:

        return False



    return bool(re.search(r"[\u0B80-\u0BFF]", str(text)))





def normalize_language(language, question=""):
    """Normalize dropdown values while preserving auto language detection."""
    requested = str(language or "auto").strip().lower()

    if requested in {"ta", "ta-in", "tamil", "தமிழ்", "tamil language", "tamil (தமிழ்)"}:
        return "ta"
    if requested in {"en", "en-in", "en-us", "en-gb", "english", "english (en)"}:
        return "en"
    if requested in {"tanglish", "ta-latn", "romanized-tamil"}:
        return "tanglish"

    detected = detect_response_language(question, "auto")
    if detected == "tamil":
        return "ta"
    if detected == "tanglish":
        return "tanglish"
    return "en"


def translate_answer(text, response_language):
    """Translate English text to the selected display language when needed."""
    if text is None or not str(text).strip():
        return text

    text = str(text)
    language = normalize_language(response_language, text)
    if language == "en":
        return text

    try:
        tamil_text = GoogleTranslator(source="auto", target="ta").translate(text)
        if not tamil_text:
            return text
        if language == "ta":
            return tamil_text
        return tamil_to_tanglish(tamil_text)
    except Exception:
        app.logger.exception("Answer translation failed")
        return text


def get_response_language(data):

    """

    Crop recommendation defaults to Tamil.

    If frontend explicitly sends English, use English.

    """



    requested_language = data.get("response_language", "en")



    return normalize_language(

        requested_language,

        data.get("question", "")

    )





# ---------------------------------------

# HOME

# ---------------------------------------



@app.route("/", methods=["GET"])

def home():

    return "AgriGpt AI Backend is Running!"





# ---------------------------------------

# STATUS

# ---------------------------------------



@app.route("/api/status", methods=["GET"])

def status():

    return jsonify({

        "project": "AgriGpt AI",

        "status": "Backend is working",

        "message": "AI Agriculture Assistant is ready"

    })





# ---------------------------------------

# AGRICULTURE AI CHAT

# ---------------------------------------



@app.route("/api/ask", methods=["POST"])

def ask_ai():

    try:

        data = request.get_json(silent=True) or {}



        question = str(data.get("question", "")).strip()



        original_question = str(

            data.get("original_question", question)

        ).strip()



        agriculture_topic = str(

            data.get("agriculture_topic", "")

        ).strip()



        question_type = str(

            data.get("question_type", "")

        ).strip()



        requested_language = data.get("response_language", "auto")



        if not question:

            return jsonify({

                "success": False,

                "answer": "Please ask an agriculture-related question."

            }), 400



        response_language = normalize_language(

            requested_language,

            original_question or question

        )



        parameters = inspect.signature(

            search_knowledge

        ).parameters



        accepts_extra_arguments = any(

            parameter.kind == inspect.Parameter.VAR_KEYWORD

            for parameter in parameters.values()

        )



        language_arguments = {}



        if (

            "response_language" in parameters

            or accepts_extra_arguments

        ):

            language_arguments["response_language"] = response_language



        if (

            "original_question" in parameters

            or accepts_extra_arguments

        ):

            language_arguments["original_question"] = (

                original_question or question

            )



        knowledge = search_knowledge(

            question,

            **language_arguments

        )



        if not knowledge:

            knowledge = (

                "I could not find specific agriculture knowledge. "

                "Please ask about crops, soil, fertilizer, irrigation, "

                "pests, diseases, seeds, harvesting, weather, "

                "or farming practices."

            )



        answer = str(knowledge)
        # search_knowledge already formats normal answers in the requested language.
        # Translate only its English fallback messages to avoid translating Tamil twice.
        if response_language in ("ta", "tanglish") and not contains_tamil(answer):
            if response_language == "tanglish":
                answer = translate_answer(answer, "tanglish")
            elif answer.startswith(("I could not find", "Sorry, I could not find", "Agriculture knowledge is")):
                answer = translate_answer(answer, "ta")



        return jsonify({

            "success": True,

            "answer": answer,

            "question": original_question or question,

            "topic": agriculture_topic,

            "question_type": question_type,

            "response_language": response_language

        }), 200



    except Exception as e:

        app.logger.exception("Error in /api/ask")



        return jsonify({

            "success": False,

            "answer": (

                "Sorry, an error occurred while processing "

                "your agriculture question."

            ),

            "error": str(e)

        }), 500





# ---------------------------------------

# MODE 2 - BASIC CROP RECOMMENDATION

#

# /api/crop-recommendation

# /api/recommend-crop

# ---------------------------------------



@app.route("/api/crop-recommendation", methods=["POST"])

@app.route("/api/recommend-crop", methods=["POST"])

def recommend_crop_basic():

    try:

        data = request.get_json(silent=True) or {}



        response_language = get_response_language(data)



        soil = str(data.get("soil", "")).strip().lower()

        season = str(data.get("season", "")).strip().lower()

        water = str(data.get("water", "")).strip().lower()



        previous_crop = str(

            data.get("previous_crop", "")

        ).strip()



        location = str(data.get("location", "")).strip()



        required_fields = {

            "soil": soil,

            "season": season,

            "water": water

        }



        missing_fields = [

            field

            for field, value in required_fields.items()

            if not value

        ]



        if missing_fields:

            message = translate_answer(

                "Please provide soil, season and water availability.",

                response_language

            )



            return jsonify({

                "success": False,

                "message": message,

                "missing_fields": missing_fields

            }), 400



        # Soil-based crop recommendation.

        if soil in [

            "clay", "clay soil", "clay-loam", "clay loam"

        ]:

            if water in ["high", "good", "available", "medium"]:

                crop = "Rice"

                reason = (

                    "Clay soil retains water and may be suitable "

                    "for rice cultivation when local conditions "

                    "are appropriate."

                )

            else:

                crop = "Millet"

                reason = (

                    "Millets may be suitable when water "

                    "availability is limited."

                )



        elif soil in ["sandy", "sandy soil"]:

            if water in ["low", "limited"]:

                crop = "Groundnut"

                reason = (

                    "Groundnut can grow in lighter soils with "

                    "suitable irrigation and nutrient management."

                )

            else:

                crop = "Vegetables"

                reason = (

                    "Some vegetables can grow in sandy soil "

                    "with proper irrigation and nutrient management."

                )



        elif soil in ["loamy", "loam", "loamy soil"]:

            crop = "Maize"

            reason = (

                "Loamy soil can support maize and many other "

                "crops when water and nutrients are managed properly."

            )



        else:

            crop = "Millet"

            reason = (

                "The most suitable crop depends on the exact "

                "soil type, local climate and water availability."

            )



        # Season adjustment.

        monsoon_seasons = [

            "kharif",

            "monsoon",

            "kharif / monsoon",

            "kharif / monsoon season"

        ]



        sufficient_water = [

            "high", "good", "available", "medium"

        ]



        clay_soils = [

            "clay", "clay soil", "clay-loam", "clay loam"

        ]



        if (

            season in monsoon_seasons

            and water in sufficient_water

            and soil in clay_soils

        ):

            crop = "Rice"

            reason = (

                "Clay soil, monsoon conditions and sufficient "

                "water can support rice cultivation."

            )



        # Keep English source fields and display the selected language.
        crop_display = translate_answer(crop, response_language)
        reason_display = translate_answer(reason, response_language)



        return jsonify({

            "success": True,

            "recommended_crop": crop_display,

            "recommended_crop_english": crop,

            "reason": reason_display,

            "reason_english": reason,

            "soil": soil,

            "season": season,

            "water_availability": water,

            "previous_crop": previous_crop,

            "location": location,

            "response_language": response_language,

            "mode": "basic"

        }), 200



    except Exception as e:

        app.logger.exception("Error in Mode 2 crop recommendation")



        return jsonify({

            "success": False,

            "message": "Unable to generate basic crop recommendation.",

            "error": str(e)

        }), 500





# ---------------------------------------

# MODE 1 - ML CROP RECOMMENDATION

#

# /api/crop-ml-recommendation

# ---------------------------------------



@app.route("/api/crop-ml-recommendation", methods=["POST"])

def crop_recommendation_module():

    try:

        data = request.get_json(silent=True) or {}



        response_language = get_response_language(data)



        required_fields = [

            "N", "P", "K", "temperature",

            "humidity", "ph", "rainfall"

        ]



        missing_fields = [

            field

            for field in required_fields

            if field not in data or data[field] in ("", None)

        ]



        if missing_fields:

            message = translate_answer(

                "Please provide all seven input values.",

                response_language

            )



            return jsonify({

                "success": False,

                "message": message,

                "missing_fields": missing_fields

            }), 400



        try:

            N = float(data["N"])

            P = float(data["P"])

            K = float(data["K"])

            temperature = float(data["temperature"])

            humidity = float(data["humidity"])

            ph = float(data["ph"])

            rainfall = float(data["rainfall"])



        except (ValueError, TypeError):

            message = translate_answer(

                "All seven input values must be numeric.",

                response_language

            )



            return jsonify({

                "success": False,

                "message": message

            }), 400



        values = [

            N, P, K, temperature,

            humidity, ph, rainfall

        ]



        if not all(math.isfinite(value) for value in values):

            message = translate_answer(

                "Please enter valid numeric values.",

                response_language

            )



            return jsonify({

                "success": False,

                "message": message

            }), 400



        if (

            N < 0 or P < 0 or K < 0

            or temperature <= 0

            or humidity <= 0 or humidity > 100

            or ph < 0 or ph > 14

            or rainfall <= 0

        ):

            message = translate_answer(

                "Please check your N, P, K, temperature, "

                "humidity, pH and rainfall values.",

                response_language

            )



            return jsonify({

                "success": False,

                "message": message

            }), 400



        if not os.path.isfile(MODEL_PATH):

            message = translate_answer(

                "Crop model file was not found.",

                response_language

            )



            return jsonify({

                "success": False,

                "message": message

            }), 500



        input_data = [[

            N, P, K, temperature,

            humidity, ph, rainfall

        ]]



        prediction = str(

            crop_model.predict(input_data)[0]

        )



        reason_english = (

            "Crop recommended using the trained "

            "Random Forest ML model."

        )



        # Keep English source fields and display the selected language.
        crop_display = translate_answer(prediction, response_language)
        reason_display = translate_answer(reason_english, response_language)



        return jsonify({

            "success": True,

            "recommended_crop": crop_display,

            "recommended_crop_english": prediction,

            "reason": reason_display,

            "reason_english": reason_english,

            "model": "Random Forest",

            "mode": "ml",

            "response_language": response_language,

            "N": N,

            "P": P,

            "K": K,

            "temperature": temperature,

            "humidity": humidity,

            "ph": ph,

            "rainfall": rainfall

        }), 200



    except Exception as e:

        app.logger.exception("Error in ML crop recommendation")



        return jsonify({

            "success": False,

            "message": "Unable to generate ML crop recommendation.",

            "error": str(e)

        }), 500





# ---------------------------------------

# RICE LEAF DISEASE DETECTION (ADDED)
# POST /api/detect-rice-disease
# Multipart image field: image

# ---------------------------------------

@app.route("/api/detect-rice-disease", methods=["POST"])
def detect_rice_disease():
    try:
        if "image" not in request.files:
            return jsonify({
                "success": False,
                "message": "Please upload an image using the 'image' field."
            }), 400

        uploaded_file = request.files["image"]

        if not uploaded_file.filename:
            return jsonify({
                "success": False,
                "message": "Please select an image file."
            }), 400

        try:
            image = Image.open(uploaded_file.stream).convert("RGB")
            image = image.resize((128, 128))
        except (UnidentifiedImageError, OSError, ValueError):
            return jsonify({
                "success": False,
                "message": "Invalid image. Please upload a valid JPG or PNG image."
            }), 400

        image_array = np.asarray(image, dtype=np.float32)
        image_array = np.expand_dims(image_array, axis=0)

        predictions = disease_model.predict(image_array, verbose=0)[0]
        best_index = int(np.argmax(predictions))
        predicted_disease = disease_class_names[best_index]
        confidence = float(predictions[best_index]) * 100

        return jsonify({
            "success": True,
            "predicted_disease": predicted_disease,
            "confidence": round(confidence, 2),
            "classes": disease_class_names,
            "message": (
                "Experimental prediction only. "
                "Please verify the result with an agricultural expert."
            )
        }), 200

    except Exception as e:
        app.logger.exception("Error in rice disease detection")
        return jsonify({
            "success": False,
            "message": "Unable to detect rice leaf disease.",
            "error": str(e)
        }), 500


# ---------------------------------------
# OPTIONAL RICE DISEASE MODEL TRAINING
# Run: python app.py --train-rice-model
# This mode does not start Flask or alter other routes.
# ---------------------------------------

def train_rice_disease_model():
    """Train a transfer-learning candidate and keep the better validation model."""
    if not os.path.isdir(DISEASE_DATASET_DIR):
        raise FileNotFoundError(
            "Rice disease dataset folder not found: " + DISEASE_DATASET_DIR
        )

    image_size = (128, 128)
    batch_size = 8
    seed = 42
    initial_epochs = 20
    fine_tune_epochs = 10

    tf.keras.utils.set_random_seed(seed)

    print("Loading rice leaf dataset...")
    train_ds = tf.keras.utils.image_dataset_from_directory(
        DISEASE_DATASET_DIR,
        validation_split=0.20,
        subset="training",
        seed=seed,
        image_size=image_size,
        batch_size=batch_size,
        label_mode="int"
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        DISEASE_DATASET_DIR,
        validation_split=0.20,
        subset="validation",
        seed=seed,
        image_size=image_size,
        batch_size=batch_size,
        label_mode="int"
    )

    class_names = train_ds.class_names
    if len(class_names) < 2:
        raise ValueError("At least two disease classes are required.")

    # Use deterministic class order from the dataset loader for this model.
    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(autotune)
    val_ds = val_ds.prefetch(autotune)

    augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.08),
        tf.keras.layers.RandomZoom(0.10),
    ], name="rice_leaf_augmentation")

    print("Loading pretrained MobileNetV2 (internet may be needed once)...")
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(128, 128, 3),
        include_top=False,
        weights="imagenet"
    )
    base_model.trainable = False

    inputs = tf.keras.Input(shape=(128, 128, 3))
    x = augmentation(inputs)
    x = tf.keras.layers.Rescaling(1.0 / 127.5, offset=-1)(x)
    x = base_model(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.30)(x)
    outputs = tf.keras.layers.Dense(
        len(class_names), activation="softmax"
    )(x)
    model = tf.keras.Model(inputs, outputs)

    phase1_path = os.path.join(DISEASE_DIR, "rice_disease_phase1_best.keras")
    phase2_path = os.path.join(DISEASE_DIR, "rice_disease_phase2_best.keras")

    def make_callbacks(checkpoint_path):
        return [
            tf.keras.callbacks.ModelCheckpoint(
                checkpoint_path,
                monitor="val_accuracy",
                mode="max",
                save_best_only=True,
                verbose=1
            ),
            tf.keras.callbacks.EarlyStopping(
                monitor="val_loss",
                patience=5,
                restore_best_weights=True,
                verbose=1
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.3,
                patience=2,
                min_lr=1e-7,
                verbose=1
            )
        ]

    print("\nPhase 1/2: training the new classification head...")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=initial_epochs,
        callbacks=make_callbacks(phase1_path)
    )

    if not os.path.isfile(phase1_path):
        raise RuntimeError("Phase 1 did not save a model checkpoint.")

    print("\nPhase 2/2: fine-tuning the final MobileNetV2 layers...")
    base_model.trainable = True
    for layer in base_model.layers[:-20]:
        layer.trainable = False
    for layer in base_model.layers:
        if isinstance(layer, tf.keras.layers.BatchNormalization):
            layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=fine_tune_epochs,
        callbacks=make_callbacks(phase2_path)
    )

    # Compare both candidates on the same validation split; keep the higher score.
    phase1_model = tf.keras.models.load_model(phase1_path)
    _, phase1_accuracy = phase1_model.evaluate(val_ds, verbose=0)
    selected_path = phase1_path
    selected_accuracy = float(phase1_accuracy)

    if os.path.isfile(phase2_path):
        phase2_model = tf.keras.models.load_model(phase2_path)
        _, phase2_accuracy = phase2_model.evaluate(val_ds, verbose=0)
        if float(phase2_accuracy) > selected_accuracy:
            selected_path = phase2_path
            selected_accuracy = float(phase2_accuracy)

    # Save as a separate candidate; never overwrite the original production model.
    shutil.copy2(selected_path, IMPROVED_DISEASE_MODEL_PATH)
    with open(IMPROVED_DISEASE_CLASS_PATH, "w", encoding="utf-8") as file:
        json.dump(class_names, file, indent=4, ensure_ascii=False)

    print("\n----------------------------------------")
    print("RICE DISEASE TRAINING FINISHED")
    print("Best validation accuracy: {:.2f}%".format(selected_accuracy * 100))
    print("Candidate model:", IMPROVED_DISEASE_MODEL_PATH)
    print("Class names:", IMPROVED_DISEASE_CLASS_PATH)
    print("Original model was not overwritten.")
    print("Restart the app to use the candidate model, then test it before relying on it.")
    print("----------------------------------------")


# ---------------------------------------

# RUN FLASK SERVER

# ---------------------------------------



if __name__ == "__main__":

    if "--train-rice-model" in sys.argv:
        train_rice_disease_model()
    else:
        app.run(
            host="127.0.0.1",
            port=5001,
            debug=True
        )


