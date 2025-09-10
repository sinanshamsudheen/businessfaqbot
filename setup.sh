#!/bin/bash

# Setup script for RAG Chatbot

echo "Setting up RAG Chatbot..."

# Create data directory
mkdir -p data

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    echo "# OpenAI API Key" > .env
    echo "OPENAI_API_KEY=your-openai-api-key-here" >> .env
    echo ""
    echo "Please update the .env file with your actual OpenAI API key"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker to run the application."
    echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
else
    echo "Docker is installed."
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose."
    echo "Visit https://docs.docker.com/compose/install/ for installation instructions."
else
    echo "Docker Compose is installed."
fi

echo ""
echo "Setup complete!"
echo "Next steps:"
echo "1. Update the .env file with your OpenAI API key"
echo "2. Place your PDF documents in the data/ directory"
echo "3. Run 'docker-compose up --build' to start the application"