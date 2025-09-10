#!/bin/bash

# Railway FastAPI Backend Startup Script
# This script properly handles PORT environment variable expansion

# Set default port if PORT is not set
if [ -z "$PORT" ]; then
    export PORT=8000
fi

echo "Starting FastAPI backend on port $PORT"

# Start uvicorn with the resolved port
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
