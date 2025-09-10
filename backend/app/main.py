from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import glob
from contextlib import asynccontextmanager

from .api import router as api_router
from .pdf_ingest import process_pdf
from .globals import faiss_store

async def auto_ingest_pdfs():
    """Automatically ingest PDFs from the data folder on startup"""
    data_folder = "data"
    if not os.path.exists(data_folder):
        print(f"Data folder {data_folder} does not exist, creating it...")
        os.makedirs(data_folder)
        return
    
    # Find all PDF files in the data folder
    pdf_files = glob.glob(os.path.join(data_folder, "*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in data folder")
        return
    
    print(f"Found {len(pdf_files)} PDF files in data folder, ingesting...")
    total_chunks = 0
    
    for pdf_file in pdf_files:
        try:
            print(f"Processing {pdf_file}...")
            chunks_count = process_pdf(pdf_file, faiss_store)
            total_chunks += chunks_count
            print(f"Successfully processed {pdf_file} - {chunks_count} chunks")
        except Exception as e:
            print(f"Error processing {pdf_file}: {str(e)}")
    
    print(f"Auto-ingestion complete. Total chunks indexed: {total_chunks}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Mi Lifestyle FAQ API...")
    await auto_ingest_pdfs()
    yield
    # Shutdown
    print("Shutting down Mi Lifestyle FAQ API...")

app = FastAPI(
    title="Mi Lifestyle FAQ API",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Mi Lifestyle FAQ API is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)