from .ollama_service import OllamaService
from .llm_service import LLMService
from .qdrant_service import QdrantService
from .rag_service import RAGService
from .travel_service import TravelService
from .itinerary_service import ItineraryService
from .chat_service import ChatService
from .flight_service import FlightService
from .hotel_service import HotelService
from .services import get_services
import logging

logger = logging.getLogger(__name__)

# Initialize services
ollama_service = OllamaService()
llm_service = LLMService(ollama_service=ollama_service)
qdrant_service = QdrantService()
rag_service = RAGService(
    llm_service=llm_service,
    qdrant_service=qdrant_service
)
travel_service = TravelService()
itinerary_service = ItineraryService()
chat_service = ChatService(
    llm_service=llm_service,
    rag_service=rag_service
)
flight_service = FlightService()
hotel_service = HotelService()

__all__ = [
    'ollama_service',
    'llm_service',
    'qdrant_service',
    'rag_service',
    'travel_service',
    'itinerary_service',
    'chat_service',
    'flight_service',
    'hotel_service',
    'get_services'
]