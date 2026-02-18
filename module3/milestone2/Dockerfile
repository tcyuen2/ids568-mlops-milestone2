# Stage 1: Builder — install Python dependencies 
FROM python:3.11-slim AS builder

WORKDIR /build

# Copy only the dependencies from requirements
COPY app/requirements.txt .

# Install packages 
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

LABEL maintainer="student@university.edu"
LABEL version="1.0.0"
LABEL description="Sentiment-analysis ML inference service"

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Copy installed packages
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY app/ .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH


EXPOSE 5000


USER appuser

# Run with gunicorn for production-grade serving
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
