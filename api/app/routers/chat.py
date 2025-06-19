from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Request, Depends
from typing import Dict, List, Any, Optional
import json
import logging
from ..models.chat import ChatMessage, ChatResponse, ConversationMessage
from ..services.ollama_service import OllamaService
from ..services.qdrant_service import QdrantService
from ..services.booking_service import BookingService
from ..services.itinerary_service import ItineraryService
from ..dependencies import get_booking_service, get_ollama_service, get_qdrant_service
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])

# Initialize services
ollama_service = get_ollama_service()
qdrant_service = get_qdrant_service()
itinerary_service = ItineraryService()

class ChatRequest(BaseModel):
    message: str
    travel_data: Optional[dict] = None

class ChatResponse(BaseModel):
    response: str
    itinerary: Optional[str] = None
    flight_results: Optional[dict] = None
    hotel_results: Optional[dict] = None

def convert_conversation_history(history: List[ConversationMessage]) -> List[Dict[str, str]]:
    """Convert conversation history to a list of dictionaries."""
    return [
        {
            "role": msg.role,
            "content": msg.content
        }
        for msg in history
    ]

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # If travel data is provided, generate itinerary
        itinerary = None
        if request.travel_data:
            itinerary = await ollama_service.generate_itinerary(request.travel_data)
            
            # Get flight and hotel results
            flight_results = await get_booking_service().search_flights(
                origin=request.travel_data.get('origin'),
                destination=request.travel_data.get('destination'),
                departure_date=request.travel_data.get('departureDate'),
                return_date=request.travel_data.get('returnDate'),
                adults=request.travel_data.get('adults'),
                travel_class=request.travel_data.get('travelClass')
            )
            
            hotel_results = await get_booking_service().search_hotels(
                location=request.travel_data.get('location'),
                check_in=request.travel_data.get('checkIn'),
                check_out=request.travel_data.get('checkOut'),
                adults=request.travel_data.get('adults'),
                room_qty=request.travel_data.get('roomQty')
            )
            
            return ChatResponse(
                response="Here's your personalized travel plan!",
                itinerary=itinerary,
                flight_results=flight_results,
                hotel_results=hotel_results
            )
        
        # If no travel data, just handle the chat message
        response = await ollama_service.generate_response(request.message)
        return ChatResponse(response=response)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details available'}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=Dict[str, Any])
async def get_chat_history(
    ollama_service: OllamaService = Depends(get_ollama_service)
) -> Dict[str, Any]:
    """Get chat history."""
    try:
        history = await ollama_service.get_chat_history()
        return {
            "status": "success",
            "history": history
        }
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting chat history: {str(e)}"
        )

@router.post("/", response_model=Dict[str, Any])
async def send_message(
    chat_message: ChatMessage,
    ollama_service: OllamaService = Depends(get_ollama_service)
) -> Dict[str, Any]:
    """Send a message and get a response."""
    try:
        if not chat_message.message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )

        response = await ollama_service.generate_response(chat_message.message)
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error sending message: {str(e)}"
        )

@router.delete("/", response_model=Dict[str, Any])
async def clear_chat_history(
    ollama_service: OllamaService = Depends(get_ollama_service)
) -> Dict[str, Any]:
    """Clear chat history."""
    try:
        await ollama_service.clear_chat_history()
        return {
            "status": "success",
            "message": "Chat history cleared successfully"
        }
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing chat history: {str(e)}"
        ) 