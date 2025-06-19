import httpx
import logging
from typing import Dict, Any, List, Optional
import json
from app.config import settings
import aiohttp
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import Ollama
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from json_repair import repair_json

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url="http://ollama:11434", timeout=300.0)
        self._ready = False
        self.model_name = "mistral:7b-instruct"
        self.chat_history: List[Dict[str, str]] = []
        self._cleanup_task = None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _pull_model(self):
        """Pull the model with retries."""
        try:
            logger.info(f"Pulling model {self.model_name}...")
            async with self.client.stream(
                "POST",
                "/api/pull",
                json={"name": self.model_name}
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if data.get("status") == "success":
                                logger.info(f"Model {self.model_name} pulled successfully")
                                return data
                            elif data.get("status") == "error":
                                logger.error(f"Error pulling model: {data.get('error')}")
                                raise Exception(data.get('error'))
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse response line: {line}")
                            continue
                        except Exception as e:
                            logger.error(f"Error processing model pull response: {str(e)}")
                            raise
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while pulling model: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error pulling model: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, json.JSONDecodeError))
    )
    async def _test_model(self) -> bool:
        """Test if the model is working with a simple request."""
        try:
            logger.info("Testing model with simple request...")
            response = await self.client.post(
                "/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": "Say hello",
                    "stream": False,
                    "options": {
                        "num_gpu": 0,  # Use CPU for test
                        "num_thread": 1,
                        "num_ctx": 128,  # Small context for test
                        "num_batch": 8,  # Small batch for test
                        "num_predict": 1  # Minimal prediction
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            if "response" in result:
                logger.info("Model test successful")
                return True
            logger.warning("Model test response missing 'response' field")
            return False
        except Exception as e:
            logger.error(f"Model test failed: {str(e)}")
            raise

    async def _cleanup_gpu_memory(self):
        """Clean up GPU memory by making a lightweight request."""
        try:
            await self.client.post(
                "/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": "cleanup",
                    "stream": False,
                    "options": {
                        "num_gpu": 0,  # Force CPU usage for cleanup
                        "num_thread": 1
                    }
                }
            )
            logger.info("GPU memory cleanup completed")
        except Exception as e:
            logger.warning(f"Error during GPU cleanup: {str(e)}")

    async def initialize(self):
        """Initialize the Ollama service."""
        try:
            logger.info("Initializing Ollama service...")
            
            # Check if model exists
            response = await self.client.get("/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            
            if not any(model["name"] == self.model_name for model in models):
                logger.info(f"Model {self.model_name} not found, pulling it...")
                await self._pull_model()
            else:
                logger.info(f"Model {self.model_name} already exists")
            
            # Wait a bit for the model to be fully loaded
            await asyncio.sleep(2)
            
            # Test the model
            if await self._test_model():
                self._ready = True
                logger.info("Ollama service initialized successfully")
            else:
                raise RuntimeError("Model test failed")
                
        except Exception as e:
            logger.error(f"Error initializing Ollama service: {str(e)}")
            self._ready = False
            raise

    def is_ready(self) -> bool:
        """Check if the service is ready."""
        return self._ready

    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response using the Ollama model."""
        if not self._ready:
            raise RuntimeError("Ollama service is not initialized")

        try:
            logger.info(f"Generating response for prompt: {prompt[:100]}...")
            
            # Add GPU memory management options
            options = {
                "num_gpu": 1,  # Use GPU
                "num_thread": 4,  # Use multiple threads
                "num_ctx": 4096,  # Context window size
                "num_batch": 512,  # Batch size
                "num_gqa": 8,  # Grouped-query attention
                "rope_scaling": None,  # No rope scaling
                "num_keep": 0,  # Don't keep any tokens
                "seed": 0,  # Random seed
                "num_predict": 128,  # Number of tokens to predict
                "temperature": 0.7,  # Temperature for sampling
                "top_p": 0.9,  # Top-p sampling
                "top_k": 40,  # Top-k sampling
                "repeat_penalty": 1.1,  # Repeat penalty
                "repeat_last_n": 64,  # Number of tokens to look back for repeat penalty
                "mirostat": 0,  # Disable mirostat
                "mirostat_tau": 5.0,  # Mirostat tau
                "mirostat_eta": 0.1,  # Mirostat eta
                "tfs_z": 1,  # Tail free sampling
                "typical_p": 1,  # Typical sampling
                "stop": None,  # No stop sequences
                **kwargs.get("options", {})
            }
            
            response = await self.client.post(
                "/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": options
                }
            )
            response.raise_for_status()
            result = response.json()
            logger.info("Response generated successfully")
            
            # Schedule cleanup after response
            asyncio.create_task(self._cleanup_gpu_memory())
            
            return result
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    def clear_history(self):
        """Clear the chat history."""
        self.chat_history = []

    async def generate_itinerary(self, travel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a travel itinerary based on the provided data."""
        if not self._ready:
            raise RuntimeError("Ollama service is not initialized")
            
        try:
            # Clear previous chat history
            self.clear_history()
            
            # Create a detailed prompt for the itinerary
            prompt = f"""Generate a detailed travel itinerary for a trip to Ireland with the following details:
            - Origin: {travel_data['originCountry']}
            - Arrival Date: {travel_data['arrivalDate']}
            - Departure Date: {travel_data['departureDate']}
            - Duration: {travel_data['duration']} days
            - Number of Adults: {travel_data['adults']}
            - Number of Children: {travel_data['children']}
            - Travel Class: {travel_data['travelClass']}
            - Budget: {travel_data['budget']}
            - Preferred Counties: {', '.join(travel_data['preferredCounties']) if travel_data['preferredCounties'] else 'No specific preferences'}
            - Accommodation Type: {travel_data['accommodationType']}
            - Transportation: {travel_data['transportation']}
            - Dietary Restrictions: {', '.join(travel_data['dietaryRestrictions']) if travel_data['dietaryRestrictions'] else 'None'}
            - Accessibility Needs: {'Yes' if travel_data['accessibility'] else 'No'}
            - Special Requirements: {travel_data['specialRequirements']}

            Please provide a day-by-day itinerary that includes:
            1. Recommended activities and attractions
            2. Suggested accommodations
            3. Transportation options between locations
            4. Estimated costs
            5. Local tips and recommendations
            6. Weather considerations
            7. Cultural events or festivals during the visit
            8. Family-friendly activities (if children are included)
            9. Accessibility information (if needed)
            10. Dietary options based on restrictions

            Format the response as a structured JSON object with the following keys:
            - itinerary: A list of daily activities and recommendations
            - county_dates: A mapping of counties to visit dates
            - total_estimated_cost: The total estimated cost of the trip
            - weather_considerations: General weather information for the travel period
            - local_tips: Important local information and tips
            """

            # Generate the response
            response = await self.generate(prompt)
            
            # Parse the response as JSON
            try:
                import json
                itinerary_data = json.loads(response)
                return itinerary_data
            except json.JSONDecodeError:
                logger.error("Failed to parse itinerary response as JSON")
                # Try to repair the JSON and parse again
                repaired = repair_json(response)
                try:
                    itinerary_data = json.loads(repaired)
                    return itinerary_data
                except Exception:
                    raise ValueError("Invalid itinerary response format, even after repair")
                
        except Exception as e:
            logger.error(f"Error generating itinerary: {str(e)}")
            raise

    def create_chain(self, model: str, system_prompt: str) -> Any:
        """Create a chain for the specified model."""
        if not self._ready:
            raise Exception("Ollama service is not ready")
            
        return {
            "model": model,
            "system_prompt": system_prompt,
            "base_url": self.client.base_url,
            "client": self.client
        }

    async def get_response(self, prompt: str, model: str = "llama2") -> str:
        """Get a response from the Ollama model."""
        if not self._ready:
            raise Exception("Ollama service is not ready")
            
        try:
            response = await self.client.post(
                f"{self.client.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            logger.error(f"Error getting response from Ollama: {str(e)}")
            raise

    async def get_chat_history(self) -> List[Dict[str, str]]:
        """Get the chat history."""
        return self.chat_history

    async def close(self):
        """Close the Ollama service."""
        self._ready = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
        await self.client.aclose()

# Create a singleton instance
ollama_service = OllamaService()

def get_ollama_service() -> OllamaService:
    """Get the singleton Ollama service instance."""
    return ollama_service 