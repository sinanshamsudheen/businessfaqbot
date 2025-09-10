#!/bin/bash

# Railway Streamlit Startup Script
# This script properly handles PORT environment variable expansion

# Set default port if PORT is not set
if [ -z "$PORT" ]; then
    export PORT=8501
fi

echo "Starting Streamlit on port $PORT"

# Start Streamlit with the resolved port
exec streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
