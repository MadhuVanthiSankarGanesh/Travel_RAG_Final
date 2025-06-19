from fastapi import APIRouter, HTTPException
from typing import Dict
from app.services import ollama_service

router = APIRouter(prefix="/api/health", tags=["health"])
 
@router.get("")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}

@router.get("/ollama")
async def ollama_health() -> Dict[str, bool]:
    """Check if Ollama service is ready."""
    return {"ready": ollama_service.is_ready()} 