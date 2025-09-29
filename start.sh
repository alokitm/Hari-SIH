#!/bin/bash
# Railway startup script for Streamlit

# Set default port if not provided
PORT=${PORT:-8501}

echo "Starting Streamlit on port $PORT"

# Check if models are available and create fallback if needed
echo "Checking model availability..."
if [ ! -f "models/railway_fallback_model.pkl" ] && [ ! -f "models/corrected_optimized_dual_target_model.pkl" ]; then
    echo "Creating fallback model for Railway deployment..."
    python create_fallback_model.py
fi

# Run Streamlit with the correct port
exec streamlit run app/app.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false