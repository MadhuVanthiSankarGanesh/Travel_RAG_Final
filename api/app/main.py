from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
from .models.chat import ChatMessage, ChatResponse
import logging
import traceback
import json
from app.routers import chat, health, travel, itinerary, flights, hotels
from app.dependencies import get_ollama_service, get_qdrant_service
from app.services import (
    ollama_service,
    llm_service,
    qdrant_service,
    rag_service,
    travel_service,
    itinerary_service,
    chat_service,
    flight_service,
    hotel_service
)
from datetime import datetime
from app.config import settings
import uvicorn
from json_repair import repair_json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
logger.info("Loading environment variables...")

# Define response models
class HealthCheckResponse(BaseModel):
    status: str
    ollama: str
    qdrant: str
    details: Optional[str] = None

app = FastAPI(
    title="Travel RAG API",
    description="API for travel planning with RAG capabilities",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # In production, you should restrict this
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        logger.info("Starting service initialization...")
        # Initialize Ollama service first
        logger.info("Initializing Ollama service...")
        await ollama_service.initialize()
        logger.info(f"Ollama service ready: {ollama_service.is_ready()}")
        
        # Initialize LLM service (depends on Ollama)
        logger.info("Initializing LLM service...")
        await llm_service.initialize()
        
        # Initialize Qdrant service
        logger.info("Initializing Qdrant service...")
        await qdrant_service.initialize()
        
        # Initialize RAG service (depends on LLM and Qdrant)
        logger.info("Initializing RAG service...")
        await rag_service.initialize()
        
        # Initialize remaining services
        logger.info("Initializing remaining services...")
        await travel_service.initialize()
        await itinerary_service.initialize()
        await chat_service.initialize()
        await flight_service.initialize()
        await hotel_service.initialize()
        
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.error(f"Ollama service ready after error: {ollama_service.is_ready()}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    try:
        # Close all services
        await ollama_service.close()
        await llm_service.close()
        await qdrant_service.close()
        await rag_service.close()
        await travel_service.close()
        await itinerary_service.close()
        await chat_service.close()
        await flight_service.close()
        await hotel_service.close()
        
        logger.info("All services closed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
        raise

# Store active WebSocket connections
active_connections: list[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    # Try to repair the JSON and parse again
                    repaired = repair_json(data)
                    try:
                        message = json.loads(repaired)
                    except Exception:
                        await websocket.send_json({"error": "Invalid JSON format, even after repair"})
                        continue
                
                # Process the message
                if message.get("type") == "chat":
                    query = message.get("query", "")
                    if not query:
                        await websocket.send_json({"error": "No query provided"})
                        continue
                    
                    try:
                        # Get response from Ollama
                        response = await ollama_service.get_response(query)
                        await websocket.send_json({
                            "type": "response",
                            "content": response
                        })
                    except Exception as e:
                        logger.error(f"Error processing chat message: {str(e)}")
                        await websocket.send_json({
                            "type": "error",
                            "content": f"Error processing your request: {str(e)}"
                        })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "content": f"An error occurred: {str(e)}"
                })
    finally:
        active_connections.remove(websocket)

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(travel.router, prefix="/api", tags=["travel"])
app.include_router(itinerary.router, prefix="/api/itinerary", tags=["itinerary"])
app.include_router(flights.router)
app.include_router(hotels.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Ireland Travel API"}

@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check():
    """Check the health of all services"""
    status = {
        "status": "ok",
        "ollama": "unknown",
        "qdrant": "unknown",
        "details": None
    }
    
    # Test Ollama Service
    try:
        test_response = await ollama_service.get_response("Test")
        status["ollama"] = "ok"
    except Exception as e:
        status.update({
            "ollama": "error",
            "status": "error",
            "details": f"Ollama connection failed: {str(e)}"
        })
        logger.error(f"Ollama health check failed: {str(e)}")
    
    # Test Qdrant Service
    try:
        await qdrant_service.search_similar("test")
        status["qdrant"] = "ok"
    except Exception as e:
        status.update({
            "qdrant": "error",
            "status": "error",
            "details": f"Qdrant connection failed: {str(e)}"
        })
        logger.error(f"Qdrant health check failed: {str(e)}")
    
    return status

class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []

class ChatResponse(BaseModel):
    response: str
    sources: List[dict] = []

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Get response from LLM service
        response = await llm_service.get_chat_response(
            request.message,
            request.history
        )
        
        # Get relevant documents from Qdrant
        relevant_docs = await qdrant_service.search(
            request.message,
            limit=3
        )
        
        return ChatResponse(
            response=response,
            sources=[{"content": doc.page_content, "metadata": doc.metadata} for doc in relevant_docs]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class TravelRequest(BaseModel):
    origin: str
    destination: str
    departureDate: Optional[datetime] = None
    returnDate: Optional[datetime] = None
    adults: int
    children: List[str]
    travelClass: str
    location: str
    checkIn: Optional[datetime] = None
    checkOut: Optional[datetime] = None
    roomQty: int
    currencyCode: str
    languageCode: str
    locationCode: str
    stops: str
    sort: str
    selectedInterests: List[str]

@app.post("/api/travel")
async def create_travel_plan(request: TravelRequest):
    try:
        # Get response from LLM service
        response = await llm_service.get_travel_plan(
            request.dict()
        )
        
        # Get relevant documents from Qdrant
        relevant_docs = await qdrant_service.search(
            f"Travel plan for {request.destination} with interests: {', '.join(request.selectedInterests)}",
            limit=3
        )
        
        return {
            "plan": response,
            "sources": [{"content": doc.page_content, "metadata": doc.metadata} for doc in relevant_docs]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        timeout_keep_alive=180,  # 3 minute timeout
        timeout_graceful_shutdown=180  # 3 minute graceful shutdown
    )