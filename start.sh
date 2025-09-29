#!/bin/bash
# Railway startup script for Streamlit with enhanced debugging

# Environment debugging
echo "=== Railway Deployment Debug Info ==="
echo "PORT: $PORT"
echo "RAILWAY_ENVIRONMENT: $RAILWAY_ENVIRONMENT"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Available files: $(ls -la)"
echo "========================================"

# Set default port if not provided
PORT=${PORT:-8501}
echo "Using port: $PORT"

# Validate port is numeric
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "ERROR: PORT is not a valid number: $PORT"
    echo "Falling back to default port 8501"
    PORT=8501
fi

# Check if models are available and create fallback if needed
echo "Checking model availability..."
if [ ! -f "models/railway_fallback_model.pkl" ] && [ ! -f "models/corrected_optimized_dual_target_model.pkl" ]; then
    echo "Creating fallback model for Railway deployment..."
    python create_fallback_model.py || echo "Warning: Failed to create fallback model"
fi

# Ensure the app directory exists and is accessible
if [ ! -f "app/app.py" ]; then
    echo "ERROR: app/app.py not found!"
    echo "Directory contents:"
    ls -la
    exit 1
fi

echo "Starting Streamlit on port $PORT..."

# Run Streamlit with enhanced configuration for Railway
exec streamlit run app/app.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --server.maxUploadSize 200 \
    --server.enableWebsocketCompression false \
    --logger.level debug