
import os
import math
import inspect
import re

from flask import Flask, jsonify, request
from flask_cors import CORS
from knowledge import search_knowledge
from crop_recommendation import recommend_crop
import joblib
from deep_translator import GoogleTranslator


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
# LANGUAGE HELPER FUNCTIONS
# ---------------------------------------

def contains_tamil(text):
    if not text:
        return False

    return bool(re.search(r"[\u0B80-\u0BFF]", str(text)))


def normalize_language(language, question=""):
    language = str(language or "auto").strip().lower()

    tamil_options = [
        "ta", "ta-in", "tamil", "தமிழ்",
        "tamil language", "tamil (தமிழ்)"
    ]

    english_options = [
        "en", "en-in", "en-us", "en-gb",
        "english", "english (en)"
    ]

    if language in tamil_options:
        return "ta"

    if language in english_options:
        return "en"

    if contains_tamil(question):
        return "ta"

    return "en"


def translate_answer(text, response_language):
    if text is None or not str(text).strip():
        return text

    language = str(response_language or "en").strip().lower()

    if language in ["en", "english"]:
        return text

    if language in ["ta", "tamil"]:
        try:
            translated = GoogleTranslator(
                source="auto",
                target="ta"
            ).translate(str(text))

            return translated or text

        except Exception:
            app.logger.exception("Tamil translation failed")
            return str(text)

    return text


def get_response_language(data):
    """
    Crop recommendation defaults to Tamil.
    If frontend explicitly sends English, use English.
    """

    requested_language = data.get("response_language", "ta")

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

        answer = translate_answer(
            str(knowledge),
            response_language
        )

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

        # Preserve English fields and add Tamil display fields.
        crop_tamil = translate_answer(crop, "ta")
        reason_tamil = translate_answer(reason, "ta")

        crop_display = (
            crop_tamil if response_language == "ta" else crop
        )

        reason_display = (
            reason_tamil if response_language == "ta" else reason
        )

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

        # Translate crop name and explanation.
        crop_tamil = translate_answer(prediction, "ta")
        reason_tamil = translate_answer(reason_english, "ta")

        crop_display = (
            crop_tamil if response_language == "ta" else prediction
        )

        reason_display = (
            reason_tamil if response_language == "ta"
            else reason_english
        )

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
# RUN FLASK SERVER
# ---------------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )

