from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.task import TaskStatus

class TaskCreate(BaseModel):
    description: str = Field(..., min_length=10)
    task_metadata: Optional[Dict[str, Any]] = {}

class TaskResponse(BaseModel):
    id: UUID
    description: str
    status: TaskStatus
    created_agent_id: Optional[UUID]
    result: Dict[str, Any]
    error: Optional[str]
    task_metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
