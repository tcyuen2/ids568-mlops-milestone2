"""
Unit tests for the ML Sentiment Inference Service.

Tests cover:
  - Health endpoint
  - Prediction endpoint (positive, negative, neutral)
  - Input validation / error handling
  - Root info endpoint
"""

import sys
import os
import pytest

# Ensure the app directory is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from app import app, predict_sentiment


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Create a Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


# ---------------------------------------------------------------------------
# Prediction endpoint — happy paths
# ---------------------------------------------------------------------------

def test_predict_positive(client):
    response = client.post("/predict", json={"text": "This movie is great and amazing"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["label"] == "positive"
    assert 0.0 <= data["confidence"] <= 1.0


def test_predict_negative(client):
    response = client.post("/predict", json={"text": "This movie is terrible and awful"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["label"] == "negative"
    assert 0.0 <= data["confidence"] <= 1.0


def test_predict_neutral(client):
    response = client.post("/predict", json={"text": "The sky is blue today"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["label"] == "neutral"
    assert data["confidence"] == 0.50


# ---------------------------------------------------------------------------
# Prediction endpoint — error handling
# ---------------------------------------------------------------------------

def test_predict_missing_text_field(client):
    response = client.post("/predict", json={"wrong_key": "hello"})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_predict_empty_text(client):
    response = client.post("/predict", json={"text": "   "})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_predict_no_json_body(client):
    response = client.post("/predict", data="not json", content_type="text/plain")
    assert response.status_code == 400


def test_predict_text_not_string(client):
    response = client.post("/predict", json={"text": 12345})
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert "service" in data
    assert "endpoints" in data


# ---------------------------------------------------------------------------
# Unit test for predict_sentiment function directly
# ---------------------------------------------------------------------------

def test_predict_sentiment_function_positive():
    result = predict_sentiment("This is excellent and wonderful")
    assert result["label"] == "positive"


def test_predict_sentiment_function_negative():
    result = predict_sentiment("This is horrible and boring")
    assert result["label"] == "negative"


def test_predict_sentiment_function_neutral():
    result = predict_sentiment("The table is made of wood")
    assert result["label"] == "neutral"
    assert result["confidence"] == 0.50