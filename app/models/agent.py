from sqlalchemy import Column, String, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.core.database import Base

class AgentType(str, enum.Enum):
    RESEARCHER = "researcher"
    CODER = "coder"
    ANALYST = "analyst"
    WRITER = "writer"
    MARKETER = "marketer"
    DEBUGGER = "debugger"
    REVIEWER = "reviewer"
    CUSTOM = "custom"

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    agent_type = Column(SQLEnum(AgentType), nullable=False)
    description = Column(Text)
    system_prompt = Column(Text, nullable=False)
    capabilities = Column(JSON, default=list)
    model = Column(String(100), default="llama-3.3-70b-versatile")
    temperature = Column(String(10), default="0.7")
    max_tokens = Column(String(10), default="2000")
    agent_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
