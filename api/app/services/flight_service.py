import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .booking_service import BookingService

logger = logging.getLogger(__name__)

class FlightService:
    def __init__(self):
        self.booking_service = BookingService()
        self._ready = False

    async def initialize(self):
        """Initialize the flight service."""
        try:
            self._ready = True
            logger.info("Flight service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing flight service: {str(e)}")
            self._ready = False
            raise

    def is_ready(self) -> bool:
        """Check if the flight service is ready."""
        return self._ready

    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        children: List[int] = None,
        travel_class: str = "ECONOMY"
    ) -> Dict[str, Any]:
        """Search for flights."""
        if not self.is_ready():
            raise RuntimeError("Flight service is not initialized")
            
        try:
            return await self.booking_service.search_flights(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                adults=adults,
                children=children,
                travel_class=travel_class
            )
        except Exception as e:
            logger.error(f"Error searching flights: {str(e)}")
            raise

    async def get_flight_details(self, flight_id: str) -> Dict[str, Any]:
        """Get details for a specific flight."""
        if not self.is_ready():
            raise RuntimeError("Flight service is not initialized")
            
        try:
            # Basic response structure
            return {
                "flight_id": flight_id,
                "airline": "Sample Airline",
                "departure": {
                    "airport": "DUB",
                    "time": "10:00",
                    "date": "2025-06-20"
                },
                "arrival": {
                    "airport": "JFK",
                    "time": "12:00",
                    "date": "2025-06-20"
                },
                "duration": "2h 00m",
                "price": {
                    "amount": 299.99,
                    "currency": "EUR"
                }
            }
        except Exception as e:
            logger.error(f"Error getting flight details: {str(e)}")
            raise

    async def close(self):
        """Close the flight service."""
        self._ready = False 