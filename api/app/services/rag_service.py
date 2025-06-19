import logging
from typing import Dict, Any, List, Optional
from .llm_service import LLMService
from .qdrant_service import QdrantService

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, llm_service: LLMService, qdrant_service: QdrantService):
        self.llm_service = llm_service
        self.qdrant_service = qdrant_service
        self._ready = False

    async def initialize(self):
        """Initialize the RAG service."""
        try:
            self._ready = True
            logger.info("RAG service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing RAG service: {str(e)}")
            self._ready = False
            raise

    def is_ready(self) -> bool:
        """Check if the RAG service is ready."""
        return self._ready

    async def generate_response(self, query: str, context: Optional[str] = None) -> str:
        """Generate a response using RAG."""
        if not self.is_ready():
            raise RuntimeError("RAG service is not initialized")
            
        try:
            # Search for relevant documents
            documents = await self.qdrant_service.search(query)
            
            # Combine document content for context
            combined_context = "\n".join([doc.page_content for doc in documents])
            
            # Generate response using LLM with context
            response = await self.llm_service.generate_response(query, combined_context)
            
            return response
        except Exception as e:
            logger.error(f"Error generating RAG response: {str(e)}")
            raise

    async def close(self):
        """Close the RAG service."""
        self._ready = False 