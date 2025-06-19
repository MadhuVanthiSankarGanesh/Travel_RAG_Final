from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.services.ollama_service import OllamaService
from app.dependencies import get_ollama_service
from datetime import datetime
import logging
import json
from ..services import get_services

logger = logging.getLogger(__name__)

router = APIRouter()

class FlightOption(BaseModel):
    status: bool
    message: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None

class HotelOption(BaseModel):
    status: bool
    message: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None

class TravelData(BaseModel):
    origin_airport: str  # IATA code
    destination_airport: str  # IATA code for Irish airports
    departure_date: datetime
    return_date: datetime
    number_of_adults: int
    number_of_children: int
    number_of_rooms: int
    hotel_counties: List[str]  # List of Irish counties
    counties_to_visit: List[str]  # List of Irish counties to visit
    interests: List[str]  # e.g., nature, castles, pubs
    budget: float  # Total budget in EUR
    transport_preference: str  # e.g., car_rental, public_transport

class ItineraryRequest(BaseModel):
    travelData: TravelData
    flightOptions: FlightOption
    hotelOptions: HotelOption

class ItineraryResponse(BaseModel):
    trip_summary: Dict[str, Any]
    flights: Dict[str, Any]
    hotels: List[Dict[str, Any]]
    daily_itinerary: List[Dict[str, Any]]
    budget_breakdown: Dict[str, float]
    tips: List[str]

@router.post("/itinerary", response_model=ItineraryResponse)
async def generate_itinerary(request: ItineraryRequest):
    try:
        services = await get_services()
        
        # Get response from LLM service
        response = await services.llm_service.get_travel_plan(
            request.travelData.dict()
        )
        
        # Get relevant documents from Qdrant
        relevant_docs = await services.qdrant_service.search(
            f"Travel plan for {request.travelData.destination_airport} with interests: {', '.join(request.travelData.interests)}",
            limit=3
        )
        
        # Parse the LLM response into the required JSON format
        itinerary_data = {
            "trip_summary": {
                "origin_airport": request.travelData.origin_airport,
                "destination_airport": request.travelData.destination_airport,
                "departure_date": request.travelData.departure_date.strftime("%Y-%m-%d"),
                "return_date": request.travelData.return_date.strftime("%Y-%m-%d"),
                "number_of_adults": request.travelData.number_of_adults,
                "number_of_children": request.travelData.number_of_children,
                "total_days": (request.travelData.return_date - request.travelData.departure_date).days,
                "estimated_total_cost_eur": request.travelData.budget,
                "transport_mode": request.travelData.transport_preference
            },
            "flights": request.flightOptions.data.get("flights", [])[0] if request.flightOptions.data and request.flightOptions.data.get("flights") else {},
            "hotels": request.hotelOptions.data.get("hotels", [])[0] if request.hotelOptions.data and request.hotelOptions.data.get("hotels") else {},
            "daily_itinerary": [],  # Will be populated by LLM response
            "budget_breakdown": {
                "flights": 0,
                "hotels": 0,
                "activities_and_tickets": 0,
                "transport": 0,
                "food_and_misc": 0,
                "total": request.travelData.budget
            },
            "tips": []  # Will be populated by LLM response
        }
        
        return ItineraryResponse(**itinerary_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _format_flight_options(flights: List[FlightOption]) -> str:
    """Format flight options for the prompt."""
    formatted = []
    for i, flight in enumerate(flights, 1):
        itinerary = flight.data.get('itineraries', [{}])[0]
        segments = itinerary.get('segments', [])
        
        if not segments:
            continue
            
        first_segment = segments[0]
        last_segment = segments[-1]
        
        formatted.append(f"""Flight Option {i}:
- Price: {flight.data.get('price', {}).get('total', 'N/A')} {flight.data.get('price', {}).get('currency', 'EUR')}
- Departure: {first_segment.get('departure', {}).get('at', 'N/A')} from {first_segment.get('departure', {}).get('iataCode', 'N/A')}
- Arrival: {last_segment.get('arrival', {}).get('at', 'N/A')} at {last_segment.get('arrival', {}).get('iataCode', 'N/A')}
- Duration: {itinerary.get('duration', 'N/A')}
- Airline: {first_segment.get('carrierCode', 'N/A')}
- Stops: {len(segments) - 1}""")
    
    return "\n\n".join(formatted)

def _format_hotel_options(hotels: List[HotelOption]) -> str:
    """Format hotel options for the prompt."""
    formatted = []
    for i, hotel in enumerate(hotels, 1):
        hotel_info = hotel.data.get('hotel', {})
        offers = hotel.data.get('offers', [{}])[0]
        
        formatted.append(f"""Hotel Option {i}:
- Name: {hotel_info.get('name', 'N/A')}
- Rating: {hotel_info.get('rating', 'N/A')} stars
- Location: {hotel_info.get('address', {}).get('cityName', 'N/A')}
- Price: {offers.get('price', {}).get('total', 'N/A')} {offers.get('price', {}).get('currency', 'EUR')} per night
- Room Type: {offers.get('room', {}).get('type', 'N/A')}
- Amenities: {', '.join(hotel_info.get('amenities', ['N/A']))}""")
    
    return "\n\n".join(formatted) 