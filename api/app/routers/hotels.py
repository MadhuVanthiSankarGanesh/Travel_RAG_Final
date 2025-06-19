from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from app.services.booking_service import BookingService
from app.dependencies import get_booking_service

router = APIRouter(prefix="/api/hotels", tags=["hotels"])

@router.post("/search")
async def search_hotels(
    request: Dict[str, Any],
    booking_service: BookingService = Depends(get_booking_service)
) -> Dict[str, Any]:
    """Search for hotels using Booking.com API."""
    try:
        travel_data = request.get("travelData", {})
        
        # Extract hotel search parameters
        location = travel_data.get("location")
        check_in = travel_data.get("checkIn")
        check_out = travel_data.get("checkOut")
        adults = travel_data.get("adults", 1)
        children = travel_data.get("children", [])  # List of children ages
        room_qty = travel_data.get("roomQty", 1)
        currency_code = travel_data.get("currencyCode", "USD")
        language_code = travel_data.get("languageCode", "en-us")
        location_code = travel_data.get("locationCode", "US")

        # Validate required parameters
        if not all([location, check_in, check_out]):
            raise HTTPException(
                status_code=400,
                detail="Missing required parameters: location, check_in, or check_out"
            )

        # First, search for destination ID
        location_results = await booking_service.search_destination(location, "hotels")
        
        if not location_results.get("data"):
            raise HTTPException(
                status_code=400,
                detail="Could not find valid location ID"
            )

        # Search for hotels
        hotels = await booking_service.search_hotels(
            location=location,
            check_in=check_in,
            check_out=check_out,
            adults=adults,
            children=children,
            room_qty=room_qty,
            currency_code=currency_code,
            language_code=language_code,
            location_code=location_code
        )

        return {"hotels": hotels}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/destinations")
async def search_destinations(
    query: str,
    booking_service: BookingService = Depends(get_booking_service)
) -> Dict[str, Any]:
    """Search for hotel destinations using Booking.com API."""
    try:
        results = await booking_service.search_destination(query, "hotels")
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{hotel_id}")
async def get_hotel_details(
    hotel_id: str,
    booking_service: BookingService = Depends(get_booking_service)
) -> Dict[str, Any]:
    """Get detailed information about a specific hotel."""
    try:
        hotel_details = await booking_service.get_hotel_details(hotel_id)
        return hotel_details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 