from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.services.booking_service import BookingService
from app.services.itinerary_service import ItineraryService
from app.dependencies import get_booking_service, get_itinerary_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class FlightSearchRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    adults: int = Field(default=1, ge=1, le=9)
    children: List[int] = Field(default_factory=list)
    travel_class: str = "ECONOMY"
    stops: str = "none"
    sort: str = "BEST"
    currency_code: str = "USD"

class HotelSearchRequest(BaseModel):
    location: str
    check_in: str
    check_out: str
    adults: int = Field(default=1, ge=1, le=9)
    children: List[int] = Field(default_factory=list)
    room_qty: int = Field(default=1, ge=1, le=9)
    currency_code: str = "USD"

class TravelRequest(BaseModel):
    origin_country: str
    arrival_date: str
    departure_date: str
    adults: int = Field(default=1, ge=1, le=9)
    children: int = Field(default=0, ge=0, le=9)
    travel_class: str = "ECONOMY"
    interests: Optional[List[str]] = None
    budget: Optional[str] = None
    preferred_counties: Optional[List[str]] = None
    accommodation_type: Optional[str] = None
    transportation: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None
    accessibility_needs: Optional[bool] = False
    special_requests: Optional[str] = None

@router.post("/travel/generate-itinerary", response_model=Dict[str, Any])
async def generate_itinerary(
    request: TravelRequest,
    background_tasks: BackgroundTasks,
    itinerary_service: ItineraryService = Depends(get_itinerary_service),
    booking_service: BookingService = Depends(get_booking_service)
) -> Dict[str, Any]:
    """Generate a travel itinerary with county-by-county breakdown."""
    try:
        # Convert string dates to date objects
        arrival_date = datetime.strptime(request.arrival_date, "%Y-%m-%d").date()
        departure_date = datetime.strptime(request.departure_date, "%Y-%m-%d").date()
        
        # Calculate duration in days
        duration = (departure_date - arrival_date).days
        
        if duration <= 0:
            raise HTTPException(
                status_code=400,
                detail="Departure date must be after arrival date"
            )
        
        # Prepare travel data
        travel_data = {
            "originCountry": request.origin_country,
            "arrivalDate": arrival_date,
            "departureDate": departure_date,
            "duration": duration,
            "adults": request.adults,
            "children": request.children,
            "travelClass": request.travel_class,
            "interests": request.interests or [],
            "budget": request.budget or "medium",
            "preferredCounties": request.preferred_counties or [],
            "accommodationType": request.accommodation_type or "hotel",
            "transportation": request.transportation or "rental car",
            "dietaryRestrictions": request.dietary_restrictions or [],
            "accessibility": request.accessibility_needs or False,
            "specialRequirements": request.special_requests or ""
        }
        
        # Generate the itinerary
        itinerary = await itinerary_service.generate_chunked_itinerary(travel_data)
        logger.info(f"Generated itinerary result: {itinerary}")
        
        # Start background tasks for flight and hotel searches
        background_tasks.add_task(
            booking_service.search_flights,
            origin=request.origin_country,
            destination="DUB",  # Dublin airport code
            departure_date=request.arrival_date,
            return_date=request.departure_date,
            adults=request.adults,
            children=[0] * request.children,  # Default age 0 for children
            travel_class=request.travel_class
        )
        
        # Start hotel searches for each county
        for county, dates in itinerary["county_dates"].items():
            # First search for the county destination ID
            dest_search = await booking_service.search_destination(
                query=f"{county}, Ireland",
                search_type="hotels"
            )
            
            if dest_search and "data" in dest_search and dest_search["data"]:
                dest_id = dest_search["data"][0]["dest_id"]
                background_tasks.add_task(
                    booking_service.search_hotels,
                    location=dest_id,
                    check_in=dates["start_date"],
                    check_out=dates["end_date"],
                    adults=request.adults,
                    children=[0] * request.children,
                    room_qty=1
                )
            else:
                logger.warning(f"Could not find destination ID for county: {county}")
        
        return {
            "status": "success",
            "itinerary": itinerary["itinerary"],
            "county_dates": itinerary["county_dates"]
        }
    except ValueError as e:
        logger.error(f"Invalid date format: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Please use YYYY-MM-DD format."
        )
    except Exception as e:
        logger.error(f"Error generating itinerary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating itinerary: {str(e)}"
        )

@router.post("/travel/flights", response_model=Dict[str, Any])
async def search_flights(
    request: FlightSearchRequest,
    booking_service: BookingService = Depends(get_booking_service)
) -> Dict[str, Any]:
    """Search for flights based on itinerary dates."""
    try:
        flights = await booking_service.search_flights(
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            return_date=request.return_date,
            adults=request.adults,
            children=request.children,
            travel_class=request.travel_class,
            stops=request.stops,
            sort=request.sort,
            currency_code=request.currency_code
        )
        return {"status": "success", "data": flights}
    except Exception as e:
        logger.error(f"Flight search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Flight search failed: {str(e)}"
        )

@router.post("/travel/hotels", response_model=Dict[str, Any])
async def search_hotels(
    request: HotelSearchRequest,
    booking_service: BookingService = Depends(get_booking_service)
) -> Dict[str, Any]:
    """Search for hotels in specific counties during itinerary dates."""
    try:
        # First search for the destination ID
        dest_search = await booking_service.search_destination(
            query=request.location,
            search_type="hotels"
        )
        
        if not dest_search or "data" not in dest_search or not dest_search["data"]:
            raise HTTPException(
                status_code=404,
                detail=f"Could not find destination: {request.location}"
            )
        
        dest_id = dest_search["data"][0]["dest_id"]
        
        hotels = await booking_service.search_hotels(
            location=dest_id,
            check_in=request.check_in,
            check_out=request.check_out,
            adults=request.adults,
            children=request.children,
            room_qty=request.room_qty,
            currency_code=request.currency_code
        )
        return {"status": "success", "data": hotels}
    except Exception as e:
        logger.error(f"Hotel search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Hotel search failed: {str(e)}"
        )