from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class TravelData(BaseModel):
    """Travel data model for itinerary generation."""
    originCountry: str = Field(..., description="Country of origin")
    arrivalDate: Optional[date] = Field(None, description="Arrival date in Ireland")
    departureDate: Optional[date] = Field(None, description="Departure date from Ireland")
    adults: int = Field(1, ge=1, le=9, description="Number of adults")
    children: int = Field(0, ge=0, le=9, description="Number of children")
    travelClass: str = Field("ECONOMY", description="Travel class (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST)")
    interests: Optional[list[str]] = Field(None, description="List of interests")
    budget: Optional[str] = Field(None, description="Budget range")
    duration: Optional[int] = Field(None, description="Duration of stay in days")
    preferredCounties: Optional[list[str]] = Field(None, description="Preferred counties to visit")
    accommodationType: Optional[str] = Field(None, description="Preferred accommodation type")
    transportation: Optional[str] = Field(None, description="Preferred mode of transportation")
    dietaryRestrictions: Optional[list[str]] = Field(None, description="Dietary restrictions")
    accessibility: Optional[bool] = Field(False, description="Accessibility requirements")
    specialRequirements: Optional[str] = Field(None, description="Any special requirements") 