from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseService(ABC):
    """Base class for all services in the application."""
    
    def __init__(self):
        """Initialize the service."""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize any resources needed by the service."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up any resources used by the service."""
        pass 