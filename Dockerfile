# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend-build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Final Python application
FROM python:3.12-slim
WORKDIR /app

# Install build dependencies and runtime tools like git
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    gcc \
    g++ \
    make \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/ backend/

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /frontend-build/dist/ /app/frontend/dist/

ENV PYTHONPATH=/app/backend
ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE 8000

CMD ["sh", "-c", "uvicorn dna.api.app:app --host $HOST --port $PORT"]
