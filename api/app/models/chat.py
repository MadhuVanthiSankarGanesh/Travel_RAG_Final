from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal

class ConversationMessage(BaseModel):
    role: Literal['user', 'assistant', 'system']
    content: str

class ChatMessage(BaseModel):
    content: str
    conversation_history: List[ConversationMessage] = Field(default_factory=list)

class ChatResponse(BaseModel):
    response: str
    itinerary: Optional[Dict[str, Any]] = None
    travel_info: Optional[Dict[str, Any]] = None 