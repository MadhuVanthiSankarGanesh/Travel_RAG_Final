from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from ..dependencies import get_ollama_service, get_qdrant_service
from langchain.schema import Document

class Services(BaseModel):
    llm_service: Any
    qdrant_service: Any

async def get_services() -> Services:
    llm_service = get_ollama_service()
    qdrant_service = get_qdrant_service()
    return Services(llm_service=llm_service, qdrant_service=qdrant_service)

class LLMService:
    def __init__(self):
        self.model = get_ollama_service()

    async def get_chat_response(self, message: str, history: List[Dict[str, str]]) -> str:
        # Format the chat history
        formatted_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
        
        # Create the prompt
        prompt = f"""Previous conversation:
{formatted_history}

User: {message}

Assistant:"""
        
        # Get response from the model
        response = await self.model.ainvoke(prompt)
        return response

    async def get_travel_plan(self, travel_data: Dict[str, Any]) -> str:
        # Create a prompt for the travel plan
        prompt = f"""Create a detailed travel plan for a trip with the following details:
- Origin: {travel_data['origin']}
- Destination: {travel_data['destination']}
- Travel Dates: {travel_data['departureDate']} to {travel_data['returnDate']}
- Number of Adults: {travel_data['adults']}
- Travel Class: {travel_data['travelClass']}
- Location: {travel_data['location']}
- Hotel Dates: {travel_data['checkIn']} to {travel_data['checkOut']}
- Number of Rooms: {travel_data['roomQty']}
- Interests: {', '.join(travel_data['selectedInterests'])}

Please provide a detailed day-by-day itinerary including:
1. Transportation options
2. Hotel recommendations
3. Activities and attractions based on the interests
4. Local dining recommendations
5. Estimated costs
6. Travel tips and important information

Travel Plan:"""
        
        # Get response from the model
        response = await self.model.ainvoke(prompt)
        return response

class QdrantService:
    def __init__(self):
        self.client = get_qdrant_service()

    async def search(self, query: str, limit: int = 3) -> List[Document]:
        # Search for relevant documents
        results = await self.client.search(
            collection_name="travel_docs",
            query=query,
            limit=limit
        )
        
        # Convert results to Document objects
        documents = []
        for result in results:
            doc = Document(
                page_content=result.payload.get("content", ""),
                metadata=result.payload.get("metadata", {})
            )
            documents.append(doc)
        
        return documents 