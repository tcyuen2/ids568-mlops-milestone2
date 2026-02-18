# Milestone 2 - ML Sentiment Analysis Service

![CI/CD Pipeline](https://github.com/tcyuen2/ids568-mlops-milestone2/actions/workflows/build.yml/badge.svg)

This is a simple sentiment analysis API that takes in text and tells you if it's positive, negative, or neutral. Built with Flask and Docker

## How to Run

Pull the image from the registry:

```bash
docker pull ghcr.io/tcyuen2/ids568-mlops-milestone2/ml-service:v1.0.0
```

Run it:

```bash
docker run -d -p 5000:5000 ghcr.io/tcyuen2/ids568-mlops-milestone2/ml-service:v1.0.0
```

Test it:

```bash
curl http://localhost:5000/health
curl -X POST http://localhost:5000/predict -H "Content-Type: application/json" -d '{"text": "this is great"}'
```

## Run Locally Without Docker

```bash
cd app
pip install -r requirements.txt
python app.py
```

## Run Tests

```bash
pip install pytest
pytest tests/ -v
```

## What's in This Repo

- `app/app.py` - the main Flask app
- `app/requirements.txt` - dependencies
- `tests/test_app.py` - unit tests
- `Dockerfile` - multi-stage Docker build
- `.github/workflows/build.yml` - CI/CD pipeline
- `RUNBOOK.md` - operations documentation
