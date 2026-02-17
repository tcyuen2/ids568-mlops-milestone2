"""Minimal ML Inference Service - Sentiment Analysis API."""

import os
import logging
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)

# --- Simple keyword-based "model" ---
POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "wonderful",
    "fantastic", "love", "best", "happy", "awesome",
    "brilliant", "superb", "enjoy", "liked", "perfect",
    "recommend", "outstanding", "positive", "pleasant",
}

NEGATIVE_WORDS = {
    "bad", "terrible", "awful", "horrible", "worst",
    "hate", "poor", "disappointing", "boring", "ugly",
    "negative", "annoying", "dislike", "mediocre", "fail",
    "broken", "useless", "frustrating", "dreadful",
}


def predict_sentiment(text: str) -> dict:
    """Return a sentiment prediction for the given text."""
    words = set(text.lower().split())
    pos_count = len(words & POSITIVE_WORDS)
    neg_count = len(words & NEGATIVE_WORDS)

    if pos_count > neg_count:
        label, confidence = "positive", min(0.5 + 0.1 * pos_count, 0.99)
    elif neg_count > pos_count:
        label, confidence = "negative", min(0.5 + 0.1 * neg_count, 0.99)
    else:
        label, confidence = "neutral", 0.50

    return {"label": label, "confidence": round(confidence, 2)}


@app.route("/health", methods=["GET"])
def health():
    """Health-check endpoint."""
    return jsonify({"status": "healthy"}), 200


@app.route("/predict", methods=["POST"])
def predict():
    """Predict sentiment for the provided text."""
    data = request.get_json(silent=True)

    if data is None or "text" not in data:
        logger.warning("Bad request: missing 'text' field")
        return jsonify({"error": "Request must include a 'text' field"}), 400

    text = data["text"]
    if not isinstance(text, str) or len(text.strip()) == 0:
        return jsonify({"error": "'text' must be a non-empty string"}), 400

    result = predict_sentiment(text)
    logger.info("Prediction: %s (confidence=%.2f)", result["label"], result["confidence"])
    return jsonify(result), 200


@app.route("/", methods=["GET"])
def root():
    """Landing page with basic API information."""
    return jsonify({
        "service": "ML Sentiment Inference API",
        "version": "1.0.0",
        "endpoints": {
            "/health": "GET  - Health check",
            "/predict": "POST - Sentiment prediction",
        },
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
