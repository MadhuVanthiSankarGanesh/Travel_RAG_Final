from fastapi import Depends
from typing import AsyncGenerator
import os
from app.services.booking_service import BookingService, get_booking_service as get_booking_service_impl
from app.services.ollama_service import OllamaService, get_ollama_service as get_ollama_service_impl
from app.services.qdrant_service import QdrantService
from app.services import booking_service, ollama_service, qdrant_service
from app.services.itinerary_service import ItineraryService

async def get_booking_service():
    """Get the booking service instance."""
    return get_booking_service_impl()

async def get_ollama_service() -> OllamaService:
    """Get an instance of the Ollama service."""
    return get_ollama_service_impl()

def get_qdrant_service() -> QdrantService:
    """Get the Qdrant service instance."""
    return qdrant_service

async def get_itinerary_service() -> ItineraryService:
    """Get an instance of the Itinerary service."""
    return ItineraryService() 