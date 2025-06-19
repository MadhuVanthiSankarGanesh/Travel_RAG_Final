import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .booking_service import BookingService

logger = logging.getLogger(__name__)

class HotelService:
    def __init__(self):
        self.booking_service = BookingService()
        self._ready = False

    async def initialize(self):
        """Initialize the hotel service."""
        try:
            self._ready = True
            logger.info("Hotel service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing hotel service: {str(e)}")
            self._ready = False
            raise

    def is_ready(self) -> bool:
        """Check if the hotel service is ready."""
        return self._ready

    async def search_hotels(
        self,
        location: str,
        check_in: str,
        check_out: str,
        adults: int = 1,
        children: List[int] = None,
        room_qty: int = 1,
        price_min: Optional[int] = None,
        price_max: Optional[int] = None
    ) -> Dict[str, Any]:
        """Search for hotels."""
        if not self.is_ready():
            raise RuntimeError("Hotel service is not initialized")
            
        try:
            return await self.booking_service.search_hotels(
                location=location,
                check_in=check_in,
                check_out=check_out,
                adults=adults,
                children=children,
                room_qty=room_qty,
                price_min=price_min,
                price_max=price_max
            )
        except Exception as e:
            logger.error(f"Error searching hotels: {str(e)}")
            raise

    async def get_hotel_details(self, hotel_id: str) -> Dict[str, Any]:
        """Get details for a specific hotel."""
        if not self.is_ready():
            raise RuntimeError("Hotel service is not initialized")
            
        try:
            return await self.booking_service.get_hotel_details(hotel_id)
        except Exception as e:
            logger.error(f"Error getting hotel details: {str(e)}")
            raise

    async def get_hotel_amenities(self, hotel_id: str) -> List[str]:
        """Get amenities for a specific hotel."""
        if not self.is_ready():
            raise RuntimeError("Hotel service is not initialized")
            
        try:
            # Basic response structure
            return [
                "Free WiFi",
                "Swimming Pool",
                "Fitness Center",
                "Restaurant",
                "Room Service",
                "Parking"
            ]
        except Exception as e:
            logger.error(f"Error getting hotel amenities: {str(e)}")
            raise

    async def close(self):
        """Close the hotel service."""
        self._ready = False 