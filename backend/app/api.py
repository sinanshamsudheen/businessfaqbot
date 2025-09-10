from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
import os
import shutil
from .pdf_ingest import process_pdf
from .rag import query_rag
from .config import get_settings
from .globals import faiss_store

router = APIRouter()
settings = get_settings()

class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    raw_generation: str

@router.post("/ingest")
async def ingest_pdf(files: List[UploadFile] = File(...)):
    """Ingest PDF files and store their embeddings in FAISS"""
    try:
        total_chunks = 0
        for file in files:
            # Save file temporarily
            file_path = f"data/{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Process PDF and add to FAISS
            chunks_count = process_pdf(file_path, faiss_store)
            total_chunks += chunks_count
            
            # Clean up temporary file
            os.remove(file_path)
        
        return JSONResponse(
            content={
                "status": "success", 
                "indexed_chunks": total_chunks,
                "message": f"Successfully indexed {total_chunks} chunks"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """Query the RAG system with a question"""
    try:
        answer, sources, raw_generation = query_rag(
            request.question, 
            faiss_store, 
            top_k=request.top_k
        )
        return QueryResponse(
            answer=answer,
            sources=sources,
            raw_generation=raw_generation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rebuild-index")
async def rebuild_index():
    """Rebuild the FAISS index from stored PDFs"""
    try:
        # For now, we'll just return a success message
        # In a full implementation, this would reprocess all PDFs
        return JSONResponse(
            content={
                "status": "success", 
                "message": "Index rebuild triggered"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))