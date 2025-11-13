from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse
from app.services.agent_service import agent_service
from app.models.agent import AgentType

router = APIRouter()

@router.post("/create", response_model=AgentResponse, status_code=201)
def create_agent(
    agent_data: AgentCreate, 
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    agent = agent_service.create_agent(db, agent_data, user_id)
    return agent

@router.post("/create-from-template", response_model=AgentResponse, status_code=201)
def create_agent_from_template(
    agent_type: AgentType,
    name: str,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    agent = agent_service.create_agent_from_template(db, agent_type, name, user_id, description)
    return agent

@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(
    agent_id: UUID, 
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    agent = agent_service.get_agent(db, agent_id, user_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.get("/", response_model=List[AgentResponse])
def get_all_agents(
    skip: int = 0,
    limit: int = 100,
    agent_type: Optional[AgentType] = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    agents = agent_service.get_all_agents(db, user_id, skip, limit, agent_type)
    return agents

@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: UUID,
    agent_data: AgentUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    agent = agent_service.update_agent(db, agent_id, agent_data, user_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.delete("/{agent_id}")
def delete_agent(
    agent_id: UUID, 
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    success = agent_service.delete_agent(db, agent_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent deleted successfully", "agent_id": str(agent_id)}