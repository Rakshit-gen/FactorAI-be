from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.execution import ExecutionStatus

class ExecutionCreate(BaseModel):
    agent_id: UUID
    input_data: str = Field(..., min_length=1)
    execution_metadata: Optional[Dict[str, Any]] = {}

class ExecutionResponse(BaseModel):
    id: UUID
    agent_id: UUID
    input_data: str
    status: ExecutionStatus
    output: Optional[str]
    error: Optional[str]
    execution_time: Optional[str]
    execution_metadata: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
