import logging
from typing import Dict, Any, List, Optional
from .llm_service import LLMService
from .rag_service import RAGService

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, llm_service: LLMService, rag_service: RAGService):
        self.llm_service = llm_service
        self.rag_service = rag_service
        self._ready = False

    async def initialize(self):
        """Initialize the chat service."""
        try:
            self._ready = True
            logger.info("Chat service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing chat service: {str(e)}")
            self._ready = False
            raise

    def is_ready(self) -> bool:
        """Check if the chat service is ready."""
        return self._ready

    async def generate_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a response using RAG pipeline."""
        if not self.is_ready():
            raise RuntimeError("Chat service is not initialized")
            
        try:
            # Use RAG service to generate response
            response = await self.rag_service.generate_response(message)
            return {
                "response": response,
                "context": context or {}
            }
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    async def close(self):
        """Close the chat service."""
        self._ready = False 