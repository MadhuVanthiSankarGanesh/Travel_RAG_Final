from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os

class Settings(BaseSettings):
    # Qdrant settings
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333

    # Ollama settings
    OLLAMA_HOST: str = "ollama"
    OLLAMA_PORT: int = 11434

    # Amadeus API settings
    AMADEUS_CLIENT_ID: str = ""
    AMADEUS_CLIENT_SECRET: str = ""

    # Database settings
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/travel_rag"
    
    # Ollama settings
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama2"
    
    # Redis settings
    REDIS_URL: str = "redis://redis:6379/0"
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Travel RAG API"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Booking.com API settings
    RAPIDAPI_KEY: Optional[str] = os.getenv("RAPIDAPI_KEY")
    RAPIDAPI_HOST: str = "booking-com.p.rapidapi.com"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 