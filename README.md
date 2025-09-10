# RAG Chatbot with OpenAI and FAISS

A Streamlit-based chat UI + FastAPI backend that ingests PDFs into FAISS, uses OpenAI's cost-effective models (GPT-4o-mini and text-embedding-3-small) for embeddings & response generation within a RAG flow, keeps chat memory in Streamlit session state (cleared on refresh), and is deployable to Railway.

## Features

- **Streamlit frontend**: Chat UI with file upload, memory stored in `st.session_state`
- **FastAPI backend**: Endpoints for PDF ingestion, RAG querying, and health checks
- **Vector DB**: FAISS index for efficient similarity search
- **LLM Integration**: OpenAI's cost-effective models (GPT-4o-mini for generation, text-embedding-3-small for embeddings)
- **PDF Processing**: Text extraction and intelligent chunking
- **Deployment**: Ready for Railway deployment

## Architecture

```
├─ backend/
│  ├─ app/
│  │  ├─ main.py                # FastAPI app
│  │  ├─ api.py                 # endpoints: /ingest, /query...
│  │  ├─ rag.py                 # retrieval + generation pipeline
│  │  ├─ embeddings_provider.py # wrapper for OpenAI embeddings
│  │  ├─ generator_provider.py  # wrapper for OpenAI generation
│  │  ├─ faiss_store.py         # FAISS index helper (save/load/add/query)
│  │  ├─ pdf_ingest.py          # pdf extraction + chunking
│  │  └─ config.py
│  ├─ Dockerfile
│  └─ requirements.txt
├─ frontend/
│  ├─ streamlit_app.py         # Streamlit chat UI
│  ├─ Dockerfile
│  └─ requirements.txt
├─ docker-compose.yml
├─ Procfile
└─ infra/
   └─ railway.*.toml
```

## Setup and Installation

### Prerequisites

1. Python 3.11+
2. OpenAI API key
3. Docker (for containerized deployment)

### Local Development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd rag-gemini-chatbot
   ```

2. Set up environment variables:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

3. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. Install frontend dependencies:
   ```bash
   cd ../frontend
   pip install -r requirements.txt
   ```

5. Run the backend:
   ```bash
   cd ../backend
   python -m app.main
   ```

6. In a new terminal, run the frontend:
   ```bash
   cd frontend
   streamlit run streamlit_app.py
   ```

### Using Docker

1. Build and run with docker-compose:
   ```bash
   docker-compose up --build
   ```

2. Access the applications:
   - Frontend: http://localhost:8501
   - Backend API docs: http://localhost:8000/docs

## Deployment to Railway

1. Create a new Railway project
2. Connect your GitHub repository
3. Add the `OPENAI_API_KEY` environment variable in Railway
4. Deploy!

## API Endpoints

- `POST /api/ingest` - Ingest PDF files
- `POST /api/query` - Query the RAG system
- `POST /api/rebuild-index` - Rebuild the FAISS index
- `GET /health` - Health check endpoint

## Usage

1. Upload PDF documents using the sidebar in the Streamlit app
2. Click "Ingest PDFs" to process them
3. Ask questions in the chat interface
4. Get answers based on your documents

## Project Structure

The project follows a clean architecture:

- **Backend**: FastAPI application with modular components
- **Frontend**: Streamlit application with chat interface
- **Data**: Persistent storage for FAISS index and metadata
- **Configuration**: Environment-based configuration management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

MIT License