
FROM node:20-slim AS frontend-builder

WORKDIR /frontend

# Copy frontend files
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

FROM base AS builder

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade "pip<26" "setuptools<81" wheel && \
    pip install --no-cache-dir --user --no-build-isolation -r requirements.txt

FROM base

COPY --from=builder /root/.local /root/.local
COPY --from=frontend-builder /frontend/dist /app/frontend/dist

ENV PATH=/root/.local/bin:$PATH

RUN mkdir -p /app/input /app/output /root/.cache/whisper

COPY app/ /app/app/
COPY services/ /app/services/
COPY web_app.py /app/

ENV PYTHONPATH=/app

VOLUME ["/app/input", "/app/output", "/root/.cache/whisper"]

CMD ["python", "web_app.py"]
