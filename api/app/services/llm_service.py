import json
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import Ollama
from tenacity import retry, stop_after_attempt, wait_exponential
from ..config import settings
from app.services.ollama_service import OllamaService
from app.services.qdrant_service import QdrantService

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, ollama_service: OllamaService):
        self.ollama_service = ollama_service
        self._ready = False
        self.qdrant_service = QdrantService()
        self.ollama_host = settings.OLLAMA_HOST
        self.ollama_port = settings.OLLAMA_PORT
        self.model = "mistral:7b-instruct"
        self.timeout = 300.0
        self.llm = None
        self.itinerary_chain = None
        self.chat_chain = None

    async def initialize(self):
        """Initialize the LLM service."""
        try:
            await self.ollama_service.initialize()
            self._ready = True
            logger.info("LLM service initialized successfully")
            
            # Initialize the itinerary generation chain
            self.itinerary_chain = self.ollama_service.create_chain(
                model="llama2",
                system_prompt="""You are a travel planning assistant specializing in Ireland. 
                Generate detailed day-by-day itineraries based on user preferences.
                Format the response with clear sections for each day and county visited.
                Include specific dates for each county in the format: 'County Name: Start Date - End Date'
                For each day, include:
                1. Morning activities
                2. Afternoon activities
                3. Evening activities
                4. Recommended restaurants
                5. Transportation details
                6. Estimated costs
                7. Local tips and customs."""
            )

            # Initialize the chat chain
            self.chat_chain = self.ollama_service.create_chain(
                model="llama2",
                system_prompt="""You are a helpful travel assistant for Ireland. 
                Answer questions about travel planning, attractions, and local customs.
                Be informative and friendly in your responses.
                Focus on providing practical, accurate information about:
                1. Tourist attractions
                2. Local customs and etiquette
                3. Transportation options
                4. Weather and packing tips
                5. Food and dining recommendations
                6. Safety and security advice."""
            )

            self.llm = Ollama(
                model=self.model,
                base_url=f"http://{self.ollama_host}:{self.ollama_port}",
                temperature=0.7
            )
            
            self.itinerary_prompt = PromptTemplate(
                input_variables=["travel_data"],
                template="""Generate a detailed Ireland travel itinerary with these requirements:

1. Counties to visit: {counties}
2. Travel dates: {arrival_date} to {departure_date}
3. Travelers: {adults} adults, {children} children
4. Budget: {budget}
5. Interests: {interests}

Format strictly as follows (do NOT use JSON):

County: [County Name] (Start Date - End Date)
Day 1 (Full Date):
- Morning: [Activity details]
- Afternoon: [Activity details]
- Evening: [Activity details]

[Repeat for each day]

County: [Next County Name] (Start Date - End Date)
[Continue format...]

Important rules:
- Use the exact format for county and date headers: County: [County Name] (Start Date - End Date)
- Use the exact format for day headers: Day X (Full Date):
- Do NOT include any JSON, code blocks, or extra explanations.
- Only output the itinerary in this structured text format."""
            )
            
            self.itinerary_chain = LLMChain(llm=self.llm, prompt=self.itinerary_prompt)
            
        except Exception as e:
            logger.error(f"Error initializing LLM service: {str(e)}")
            self._ready = False
            raise

    def is_ready(self) -> bool:
        """Check if the LLM service is ready."""
        return self._ready and self.ollama_service.is_ready()

    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate a response using the LLM."""
        if not self.is_ready():
            raise RuntimeError("LLM service is not initialized")
        return await self.ollama_service.generate_response(prompt, context)

    async def generate_itinerary(self, travel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a travel itinerary."""
        if not self.is_ready():
            raise RuntimeError("LLM service is not initialized")
        return await self.ollama_service.generate_chunked_itinerary(travel_data)

    async def get_chat_history(self) -> List[Dict[str, str]]:
        """Get the chat history."""
        return await self.ollama_service.get_chat_history()

    async def close(self):
        """Close the LLM service."""
        self._ready = False
        await self.ollama_service.close()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_itinerary(self, travel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a travel itinerary based on user preferences."""
        if not self.ollama_service or not self.itinerary_chain:
            raise Exception("LLM service not properly initialized")
            
        try:
            # Format the travel data
            formatted_data = self._format_travel_data(travel_data)
            
            # Generate itinerary using LLM
            response = await self.itinerary_chain.ainvoke({"travel_data": json.dumps(formatted_data, indent=2)})
            
            # Extract county dates from the response
            county_dates = self._extract_county_dates(response)
            
            return {
                "itinerary": response,
                "county_dates": county_dates,
                "original_dates": {
                    "arrival": formatted_data["arrivalDate"],
                    "departure": formatted_data["departureDate"]
                }
            }
        except Exception as e:
            logger.error(f"Error generating itinerary: {str(e)}")
            raise

    def _format_travel_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format travel data for LLM input."""
        return {
            "originCountry": data.get("origin_country", ""),
            "arrivalDate": data.get("arrival_date", ""),
            "departureDate": data.get("departure_date", ""),
            "adults": data.get("adults", 1),
            "children": data.get("children", 0),
            "travelClass": data.get("travel_class", "ECONOMY"),
            "interests": data.get("interests", []),
            "budget": data.get("budget", "medium"),
            "preferredCounties": data.get("preferred_counties", []),
            "accommodationType": data.get("accommodation_type", "hotel"),
            "transportation": data.get("transportation", "rental car"),
            "dietaryRestrictions": data.get("dietary_restrictions", []),
            "accessibility": data.get("accessibility_needs", False),
            "specialRequests": data.get("special_requests", "")
        }

    def _extract_county_dates(self, response: str) -> Dict[str, Dict[str, str]]:
        """Extract county names and dates from the LLM response (non-JSON format)."""
        pattern = r"County: ([A-Za-z\s]+) \(([^)]+) - ([^)]+)\)"
        county_dates = {}
        for match in re.finditer(pattern, response):
            county = match.group(1).strip()
            start_date = match.group(2).strip()
            end_date = match.group(3).strip()
            county_dates[county] = {
                "start_date": start_date,
                "end_date": end_date
            }
        return county_dates

    def _parse_date_string(self, date_str: str) -> Optional[str]:
        """Parse a date string into a standardized format."""
        try:
            # Try different date formats
            formats = [
                "%B %d",  # January 1
                "%B %dst",  # January 1st
                "%B %dnd",  # January 2nd
                "%B %drd",  # January 3rd
                "%B %dth",  # January 4th
            ]
            
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            
            return None
        except Exception as e:
            logger.error(f"Error parsing date string: {str(e)}")
            return None