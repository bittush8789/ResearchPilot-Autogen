# ==============================================================================
# ResearchPilot — All-in-One Standalone Dockerfile
# ==============================================================================
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    BACKEND_URL=http://127.0.0.1:8000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy all application modules
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY docker/entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh

# Create persistent storage directories
RUN mkdir -p /app/data/sessions /app/data/pdfs

EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=20s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health && curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
