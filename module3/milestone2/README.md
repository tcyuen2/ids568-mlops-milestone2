# ML Sentiment Inference Service

![CI/CD Pipeline](https://github.com/tcyuen2/ids568-mlops-milestone2/actions/workflows/build.yml/badge.svg)

A lightweight, production-ready sentiment analysis API built with Flask and deployed via a multi-stage Docker image with fully automated CI/CD.

---

## Quick Start

### Pull the pre-built image

```bash
docker pull ghcr.io/tcyuen2/ids568-mlops-milestone2/ml-service:v1.0.0
```

### Run the container

```bash
docker run -d -p 5000:5000 --name ml-service ghcr.io/tcyuen2/ids568-mlops-milestone2/ml-service:v1.0.0
```

### Test the service

```bash
# Health check
curl http://localhost:5000/health

# Predict sentiment
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "This product is absolutely wonderful"}'
```

Expected response:

```json
{"label": "positive", "confidence": 0.7}
```

---

## Local Development

### Using Docker Compose

```bash
docker compose up --build
```

### Without Docker

```bash
cd app
pip install -r requirements.txt
python app.py
```

### Running Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## API Endpoints

| Method | Path       | Description                           |
|--------|------------|---------------------------------------|
| GET    | `/`        | Service info and available endpoints  |
| GET    | `/health`  | Liveness / readiness health check     |
| POST   | `/predict` | Sentiment prediction (JSON body)      |

### POST `/predict`

**Request body:**

```json
{"text": "Your input sentence here"}
```

**Response:**

```json
{"label": "positive", "confidence": 0.80}
```

---

## Project Structure

```
module3/milestone2/
├── .github/workflows/
│   └── build.yml          # CI/CD pipeline
├── app/
│   ├── app.py             # Flask inference service
│   └── requirements.txt   # Pinned Python dependencies
├── tests/
│   └── test_app.py        # Unit tests
├── .dockerignore           # Build context exclusions
├── Dockerfile              # Multi-stage container build
├── docker-compose.yaml     # Local development helper
├── README.md               # This file
└── RUNBOOK.md              # Operations runbook
```

---

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/build.yml`) automates:

1. **Test** — installs dependencies and runs `pytest`
2. **Build** — constructs a multi-stage Docker image
3. **Authenticate** — logs in to GHCR using `GITHUB_TOKEN`
4. **Publish** — pushes the image with semantic version tags

Images are only published when tests pass and the push is to `main` or a version tag (`v*.*.*`).

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/):

```
vMAJOR.MINOR.PATCH
```

Create a new release:

```bash
git tag v1.0.0
git push --tags
```
