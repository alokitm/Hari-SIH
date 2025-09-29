#!/bin/bash
# Railway startup script for Streamlit

# Set default port if not provided
PORT=${PORT:-8501}

echo "Starting Streamlit on port $PORT"

# Run Streamlit with the correct port
exec streamlit run app/app.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false