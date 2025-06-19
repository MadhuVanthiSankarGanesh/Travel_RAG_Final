from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from app.services.booking_service import BookingService
from app.dependencies import get_booking_service

router = APIRouter(prefix="/api/flights", tags=["flights"])

@router.post("/search")
async def search_flights(
    request: Dict[str, Any],
    booking_service: BookingService = Depends(get_booking_service)
) -> Dict[str, Any]:
    """Search for flights using Booking.com API."""
    try:
        travel_data = request.get("travelData", {})
        
        # Extract flight search parameters
        origin = travel_data.get("origin")
        destination = travel_data.get("destination")
        departure_date = travel_data.get("departureDate")
        return_date = travel_data.get("returnDate")
        adults = travel_data.get("adults", 1)
        children = travel_data.get("children", [])  # List of children ages
        travel_class = travel_data.get("travelClass", "ECONOMY")
        stops = travel_data.get("stops", "none")
        sort = travel_data.get("sort", "BEST")
        currency_code = travel_data.get("currencyCode", "USD")

        # Validate required parameters
        if not all([origin, destination, departure_date, return_date]):
            raise HTTPException(
                status_code=400,
                detail="Missing required parameters: origin, destination, departure_date, or return_date"
            )

        # First, search for destination IDs
        origin_results = await booking_service.search_destination(origin, "flights")
        dest_results = await booking_service.search_destination(destination, "flights")

        if not origin_results.get("data") or not dest_results.get("data"):
            raise HTTPException(
                status_code=400,
                detail="Could not find valid airport codes for origin or destination"
            )

        # Search for flights
        flights = await booking_service.search_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=adults,
            children=children,
            travel_class=travel_class,
            stops=stops,
            sort=sort,
            currency_code=currency_code
        )

        return {"flights": flights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/destinations")
async def search_destinations(
    query: str,
    booking_service: BookingService = Depends(get_booking_service)
) -> Dict[str, Any]:
    """Search for flight destinations using Booking.com API."""
    try:
        results = await booking_service.search_destination(query, "flights")
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 