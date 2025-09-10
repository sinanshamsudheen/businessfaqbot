# 🚀 Mi Lifestyle FAQ Assistant - Railway Deployment Guide

This comprehensive guide will walk you through deploying your Mi Lifestyle FAQ Assistant on Railway, a modern cloud platform that makes deployment simple and scalable.

## 📋 Prerequisites

Before starting, ensure you have:

- [x] **Railway Account** - Sign up at [railway.app](https://railway.app)
- [x] **GitHub Repository** - Your code should be in a GitHub repository
- [x] **OpenAI API Key** - Get one from [OpenAI Platform](https://platform.openai.com/api-keys)
- [x] **Railway CLI** (Optional but recommended) - Install from [docs.railway.app/develop/cli](https://docs.railway.app/develop/cli)

## 🎯 Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │
│   (Streamlit)   │◄──►│   (FastAPI)     │
│   Port: 8501    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘
```

## 🚀 Method 1: Deploy via Railway Dashboard (Recommended)

### Step 1: Prepare Your Repository

1. **Push your code to GitHub** with the following structure:
```
Mi-Lifestyle-FAQ/
├── backend/
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── streamlit_app.py
│   ├── Dockerfile
│   └── requirements.txt
├── data/
│   └── milifestyle.pdf
├── docker-compose.yml
├── .env.example
└── RAILWAY_DEPLOYMENT.md
```

2. **Create a `.env.example` file** in your root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 2: Deploy Backend Service

1. **Login to Railway** at [railway.app](https://railway.app)

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Backend Service**
   - Railway will auto-detect your project
   - Click "Add Service" → "GitHub Repo"
   - Select your repository
   - Set **Root Directory** to `backend`
   - Railway will detect the Dockerfile automatically

4. **Set Environment Variables**
   - Go to your backend service
   - Click "Variables" tab
   - Add the following variables:
   ```
   OPENAI_API_KEY=your_actual_openai_api_key
   PORT=8000
   PYTHONUNBUFFERED=1
   ```

5. **Upload PDF Files** (Important!)
   - Railway doesn't automatically copy your local `data/` folder
   - You have two options:
   
   **Option A: Include PDFs in your repository (Recommended)**
   ```bash
   # In your local project, copy PDFs to backend folder
   cp data/*.pdf backend/data/
   
   # Update backend Dockerfile to copy these files
   # Add this line after COPY app ./app:
   # COPY data/*.pdf ./data/
   
   # Commit and push changes
   git add .
   git commit -m "Add PDF files for Railway deployment"
   git push origin main
   ```
   
   **Option B: Mount PDFs via Railway Volume (Advanced)**
   - Go to backend service → Settings → Volumes
   - Create a volume mounted to `/app/data`
   - Upload PDF files to the volume

6. **Configure Custom Start Command** (if needed)
   - In Settings → Deploy
   - Custom Start Command: `./start.sh` (uses startup script for proper port handling)

7. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Note down your backend URL (e.g., `https://your-backend.railway.app`)

### Step 3: Deploy Frontend Service

1. **Add Frontend Service**
   - In the same project, click "New Service"
   - Select "GitHub Repo"
   - Choose the same repository
   - Set **Root Directory** to `frontend`

2. **Set Environment Variables**
   - Go to your frontend service
   - Click "Variables" tab
   - Add:
   ```
   API_URL=https://your-backend.railway.app/api
   STREAMLIT_SERVER_HEADLESS=true
   STREAMLIT_SERVER_ENABLE_CORS=false
   STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
   PORT=8501
   ```

3. **Configure Custom Start Command**
   - Custom Start Command: `./start.sh` (uses startup script for proper port handling)

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete

## 🚀 Method 2: Deploy via Railway CLI

### Step 1: Install Railway CLI

```bash
# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh

# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex
```

### Step 2: Login and Initialize

```bash
# Login to Railway
railway login

# Navigate to your project directory
cd /path/to/your/Mi-Lifestyle-FAQ

# Initialize Railway project
railway init
```

### Step 3: Deploy Backend

```bash
# Create and switch to backend service
railway service create backend
railway service connect backend

# Set environment variables
railway variables set OPENAI_API_KEY=your_openai_api_key
railway variables set PORT=8000
railway variables set PYTHONUNBUFFERED=1

# Deploy backend
railway up --detach
```

### Step 4: Deploy Frontend

```bash
# Create and switch to frontend service  
railway service create frontend
railway service connect frontend

# Set environment variables
railway variables set API_URL=https://your-backend.railway.app/api
railway variables set STREAMLIT_SERVER_HEADLESS=true
railway variables set PORT=8501

# Deploy frontend
railway up --detach
```

## 🔧 Configuration Files

### Backend `railway.toml` (Optional)

Create `backend/railway.toml`:
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "./start.sh"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### Frontend `railway.toml` (Optional)

Create `frontend/railway.toml`:
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "./start.sh"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

## 📊 Environment Variables Reference

### Backend Environment Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-...` |
| `PORT` | Port for backend service | `8000` |
| `PYTHONUNBUFFERED` | Python output buffering | `1` |

### Frontend Environment Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `API_URL` | Backend API URL | `https://backend.railway.app/api` |
| `STREAMLIT_SERVER_HEADLESS` | Run Streamlit in headless mode | `true` |
| `STREAMLIT_SERVER_ENABLE_CORS` | Enable CORS | `false` |
| `PORT` | Port for frontend service | `8501` |

## 🔍 Post-Deployment Checklist

### ✅ Verify Backend Deployment

1. **Check Health Endpoint**
   ```bash
   curl https://your-backend.railway.app/health
   ```
   Expected response: `{"status": "healthy", "message": "Mi Lifestyle FAQ API is running"}`

2. **Test API Endpoint**
   ```bash
   curl -X POST https://your-backend.railway.app/api/query \
     -H "Content-Type: application/json" \
     -d '{"question": "What are the benefits of being a distributor?"}'
   ```

### ✅ Verify Frontend Deployment

1. **Access Frontend URL**
   - Visit your frontend Railway URL
   - Should see: "🏢 Mi Lifestyle FAQ Assistant"
   - Welcome message should appear

2. **Test Chat Functionality**
   - Try asking: "What products does Mi Lifestyle offer?"
   - Should receive a response from the backend

## 🚨 Troubleshooting

### Common Issues & Solutions

#### 1. **Backend Health Check Failing**
```bash
# Check logs
railway logs --service backend

# Common fixes:
# - Verify OPENAI_API_KEY is set correctly
# - Check if PDF files are being processed
# - Ensure port 8000 is properly exposed
```

#### 2. **Backend/Frontend PORT Environment Variable Error**
This error occurs when uvicorn/streamlit can't parse the PORT variable properly.

**Backend Error Message:**
```
Error: Invalid value for '--port': '$PORT' is not a valid integer.
```

**Frontend Error Message:**
```
Error: Invalid value for '--server.port': '${PORT:-8501}' is not a valid integer.
```

**Solution (Using Startup Scripts):**
Both backend and frontend now include startup scripts that properly handle PORT variable expansion:

**Backend (`backend/start.sh`):**
```bash
#!/bin/bash
if [ -z "$PORT" ]; then
    export PORT=8000
fi
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Frontend (`frontend/start.sh`):**
```bash
#!/bin/bash
if [ -z "$PORT" ]; then
    export PORT=8501
fi
exec streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

**Railway Configuration:**
- Set Custom Start Command to: `./start.sh` for both services
- No need to set PORT variables manually - Railway provides them automatically

#### 3. **Docker Build Error: "COPY ../data ./data" not found**
This error occurs when the Dockerfile tries to copy files from outside the build context.

**Solution:**
```bash
# Copy PDF files to backend directory
cp data/*.pdf backend/data/

# Update your Dockerfile to:
COPY data/ ./data/

# Commit and push changes
git add .
git commit -m "Fix PDF file copying for Railway deployment"
git push origin main
```

#### 4. **Streamlit PORT Environment Variable Error**
This error occurs when Streamlit can't parse the PORT variable properly.

**Error Message:**
```
Error: Invalid value for '--server.port': '${PORT:-8501}' is not a valid integer.
```

**Solution (Updated - Using Startup Script):**
The project now includes a `start.sh` script that properly handles PORT variable expansion:

```bash
# The start.sh script automatically handles this:
#!/bin/bash
if [ -z "$PORT" ]; then
    export PORT=8501
fi
exec streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

**Railway Configuration:**
- Set Custom Start Command to: `./start.sh`
- No need to set PORT variable manually - Railway provides it automatically
- The startup script falls back to 8501 if PORT is not set

#### 4. **Frontend Shows 502 Error - Backend Connection Failed**
This error occurs when the frontend can't reach the backend service.

**Error in Browser:**
```
Error: 502 - {"status":"error","code":502,"message":"Application failed to respond"}
```

**Debugging Steps:**

1. **Check Backend Health:**
   ```bash
   curl https://your-backend.railway.app/health
   ```
   Expected: `{"status": "healthy", "message": "Mi Lifestyle FAQ API is running"}`

2. **Check Backend Logs:**
   ```bash
   railway logs --service backend
   ```
   Look for:
   - PDF processing messages
   - OpenAI API errors
   - Port binding issues

3. **Verify Frontend API_URL:**
   - Go to frontend service → Variables
   - Ensure `API_URL=https://your-backend.railway.app/api` 
   - **Important:** Must end with `/api`, not just the domain

4. **Check CORS Settings:**
   Backend should allow frontend domain. If needed, update CORS in `backend/app/main.py`

**Quick Fix Commands:**
```bash
# Check both services are running
railway status

# Restart backend service
railway service connect backend
railway up --detach

# Check backend URL and update frontend
railway service connect frontend
railway variables set API_URL=https://your-actual-backend-url.railway.app/api
```

#### 5. **Frontend Can't Connect to Backend**
```bash
# Check frontend logs
railway logs --service frontend

# Common fixes:
# - Verify API_URL points to correct backend URL
# - Ensure backend is deployed and healthy
# - Check CORS settings
```

#### 6. **PDF Processing Issues**
```bash
# Check if data folder is properly mounted
# Verify PDF files are in the data/ directory
# Check backend logs for ingestion errors
```

#### 7. **OpenAI API Errors**
- Verify API key is valid and has credits
- Check OpenAI API usage limits
- Ensure correct model permissions

### Monitoring & Logs

```bash
# View real-time logs
railway logs --service backend --follow
railway logs --service frontend --follow

# Check service status
railway status

# View environment variables
railway variables
```

## 💰 Cost Optimization

### Railway Pricing Tips

1. **Starter Plan** ($5/month) - Good for development
2. **Pro Plan** ($20/month) - Recommended for production
3. **Resource Usage**:
   - Backend: ~256MB RAM, 0.1 vCPU
   - Frontend: ~512MB RAM, 0.1 vCPU

### OpenAI Cost Management

1. **Model Selection**: Using `gpt-4o-mini` (most cost-effective)
2. **Token Optimization**: Responses limited to 800 tokens
3. **Monitoring**: Check usage at [OpenAI Usage Dashboard](https://platform.openai.com/usage)

## 🔒 Security Best Practices

### 1. Environment Variables
- Never commit API keys to repository
- Use Railway's secure variable storage
- Rotate API keys regularly

### 2. API Security
- Backend only accepts POST requests
- CORS properly configured
- Rate limiting (if needed)

### 3. Content Security
- PDF content is processed securely
- No user data persistence
- Stateless architecture

## 🚀 Custom Domain Setup (Optional)

1. **Add Custom Domain**
   - In Railway project settings
   - Click "Domains"
   - Add your domain (e.g., `chat.milifestyle.com`)

2. **DNS Configuration**
   - Add CNAME record pointing to Railway domain
   - SSL certificate is automatically provided

## 📈 Scaling & Performance

### Auto-scaling Features
- Railway automatically scales based on demand
- Zero-downtime deployments
- Health checks and auto-restart

### Performance Optimization
- Docker image caching
- Efficient PDF processing
- OpenAI response caching (if implemented)

## 🛠️ Maintenance

### Regular Tasks
- Monitor OpenAI API usage
- Update PDF documents in data folder
- Check Railway service health
- Review application logs

### Updates & Deployments
```bash
# Deploy updates
git push origin main  # Auto-deploys if connected to GitHub

# Or using CLI
railway up
```

## 📞 Support & Resources

- **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [railway.app/discord](https://railway.app/discord)
- **OpenAI Documentation**: [platform.openai.com/docs](https://platform.openai.com/docs)

---

## 🎉 Congratulations!

Your Mi Lifestyle FAQ Assistant is now live on Railway! 🚀

**Frontend URL**: `https://your-frontend.railway.app`
**Backend URL**: `https://your-backend.railway.app`

Your customers can now access the friendly, premium Mi Lifestyle FAQ experience from anywhere in the world!
