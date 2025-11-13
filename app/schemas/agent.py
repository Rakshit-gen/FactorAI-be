from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.agent import AgentType

class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    agent_type: AgentType
    description: Optional[str] = None
    system_prompt: str = Field(..., min_length=10)
    capabilities: Optional[List[str]] = []
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.7
    max_tokens: int = 2000
    agent_metadata: Optional[Dict[str, Any]] = {}

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    capabilities: Optional[List[str]] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    agent_metadata: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    id: UUID
    name: str
    agent_type: AgentType
    description: Optional[str]
    system_prompt: str
    capabilities: List[str]
    model: str
    temperature: str
    max_tokens: str
    agent_metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
