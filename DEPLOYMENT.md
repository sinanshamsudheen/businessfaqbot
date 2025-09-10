# Railway Deployment Guide

This guide will help you deploy the RAG Chatbot application to Railway.

## Prerequisites

1. A Railway account (https://railway.app/)
2. A Google Gemini API key
3. This repository cloned locally

## Deployment Steps

### 1. Create a New Project on Railway

1. Go to https://railway.app/ and sign in to your account
2. Click on "New Project"
3. Choose "Deploy from GitHub repo" or "Deploy from CLI"

### 2. Configure Environment Variables

In your Railway project settings, add the following environment variables:

- `GEMINI_API_KEY` - Your Google Gemini API key

### 3. Deploy Using Docker

Railway will automatically detect the Dockerfiles in your project and build the containers.

### 4. Manual Deployment (Alternative)

If you prefer to deploy manually:

1. Install the Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Create a new project:
   ```bash
   railway init
   ```

4. Deploy the application:
   ```bash
   railway up
   ```

### 5. Configure Services

The application consists of two services:

1. **Backend API** (FastAPI)
   - Port: 8000
   - Health check: `/health`

2. **Frontend** (Streamlit)
   - Port: 8501

Railway will automatically assign public URLs to both services.

## Configuration

### Environment Variables

- `GEMINI_API_KEY` (required) - Your Google Gemini API key
- `API_URL` (frontend) - URL of the backend API (automatically set in docker-compose)

### Scaling

Railway automatically scales your application based on demand. You can configure scaling options in your project settings.

## Troubleshooting

### Common Issues

1. **API Key Not Set**: Make sure you've added your `GEMINI_API_KEY` to the Railway environment variables.

2. **Port Configuration**: Railway requires applications to listen on the port specified by the `$PORT` environment variable.

3. **Dependency Issues**: If you encounter dependency issues, make sure your `requirements.txt` files are up to date.

### Logs

You can view application logs directly in the Railway dashboard or using the CLI:

```bash
railway logs
```

## Updating the Application

To deploy updates:

1. Push your changes to your GitHub repository
2. Railway will automatically rebuild and deploy the updated application

Or manually with:

```bash
railway up
```