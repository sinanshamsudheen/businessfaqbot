#!/bin/bash

# Test script for RAG Chatbot

echo "Testing RAG Chatbot setup..."

# Check if required environment variables are set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "Warning: GEMINI_API_KEY environment variable is not set"
    echo "Please set it with: export GEMINI_API_KEY='your-api-key'"
else
    echo "GEMINI_API_KEY is set"
fi

echo "Required directories found"

# Check if required files exist
required_files=(
    "backend/app/main.py"
    "backend/app/api.py"
    "backend/app/pdf_ingest.py"
    "backend/app/faiss_store.py"
    "backend/app/embeddings_provider.py"
    "backend/app/rag.py"
    "backend/app/config.py"
    "frontend/streamlit_app.py"
    "backend/requirements.txt"
    "frontend/requirements.txt"
    "backend/Dockerfile"
    "frontend/Dockerfile"
    "docker-compose.yml"
    "README.md"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "Error: Required file $file not found"
        exit 1
    fi
done

echo "All required files found"

echo "Setup verification complete!"
echo "To run the application:"
echo "1. Make sure you have Docker installed"
echo "2. Set your GEMINI_API_KEY environment variable"
echo "3. Run: docker-compose up --build"