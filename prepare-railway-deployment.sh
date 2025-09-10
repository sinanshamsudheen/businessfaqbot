#!/bin/bash

# Railway Deployment Preparation Script for Mi Lifestyle FAQ Assistant

echo "🚀 Preparing Mi Lifestyle FAQ Assistant for Railway Deployment..."

# Create backend data directory if it doesn't exist
echo "📁 Creating backend data directory..."
mkdir -p backend/data

# Copy PDF files to backend data directory
echo "📄 Copying PDF files to backend data directory..."
if [ -d "data" ] && [ "$(ls -A data/*.pdf 2>/dev/null)" ]; then
    cp data/*.pdf backend/data/
    echo "✅ PDF files copied successfully"
else
    echo "⚠️  No PDF files found in data/ directory"
    echo "   Please add your PDF files to the data/ directory first"
fi

# Check if .env.example exists
if [ ! -f ".env.example" ]; then
    echo "📝 Creating .env.example file..."
    cat > .env.example << EOL
# Mi Lifestyle FAQ Assistant - Environment Variables

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Backend Configuration (for local development)
API_URL=http://localhost:8000/api

# Production Configuration (Railway deployment)
# API_URL=https://your-backend.railway.app/api
EOL
    echo "✅ .env.example created"
fi

# Verify required files exist
echo "🔍 Verifying project structure..."

required_files=(
    "backend/Dockerfile"
    "backend/requirements.txt"
    "backend/app/main.py"
    "frontend/Dockerfile"
    "frontend/requirements.txt"
    "frontend/streamlit_app.py"
    "docker-compose.yml"
)

all_files_exist=true

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = true ]; then
    echo ""
    echo "🎉 Project is ready for Railway deployment!"
    echo ""
    echo "Next steps:"
    echo "1. Push your code to GitHub"
    echo "2. Follow the RAILWAY_DEPLOYMENT.md guide"
    echo "3. Set your OPENAI_API_KEY in Railway environment variables"
else
    echo ""
    echo "❌ Some required files are missing. Please check the project structure."
fi

echo ""
echo "📚 For detailed deployment instructions, see RAILWAY_DEPLOYMENT.md"
