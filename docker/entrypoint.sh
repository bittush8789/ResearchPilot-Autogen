#!/bin/bash
set -e

echo "=================================================================="
echo "⚡ ResearchPilot — Starting Container Services"
echo "=================================================================="

# Ensure directories exist
mkdir -p /app/data/sessions /app/data/pdfs

# Start FastAPI backend in background
echo "[1/2] Starting FastAPI Backend on 0.0.0.0:8000..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to become healthy
echo "Waiting for FastAPI healthcheck..."
until curl -s http://127.0.0.1:8000/health > /dev/null; do
    sleep 1
done
echo "✓ FastAPI Backend is healthy!"

# Start Streamlit frontend in foreground
echo "[2/2] Starting Streamlit Frontend on 0.0.0.0:8501..."
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true &
FRONTEND_PID=$!

# Trap signals for graceful shutdown
trap "kill -TERM $BACKEND_PID $FRONTEND_PID" SIGINT SIGTERM

wait -n
