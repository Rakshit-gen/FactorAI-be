from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.models.agent import Agent, AgentType
from app.schemas.agent import AgentCreate, AgentUpdate
from app.agents.templates import get_template

class AgentService:
    @staticmethod
    def create_agent(db: Session, agent_data: AgentCreate) -> Agent:
        agent = Agent(
            name=agent_data.name,
            agent_type=agent_data.agent_type,
            description=agent_data.description,
            system_prompt=agent_data.system_prompt,
            capabilities=agent_data.capabilities or [],
            model="llama-3.3-70b-versatile",
            temperature=str(agent_data.temperature),
            max_tokens=str(agent_data.max_tokens),
            agent_metadata=agent_data.agent_metadata or {}
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent
    
    @staticmethod
    def create_agent_from_template(db: Session, agent_type: AgentType, name: str, description: Optional[str] = None) -> Agent:
        template = get_template(agent_type)
        
        agent = Agent(
            name=name,
            agent_type=agent_type,
            description=description or f"Agent created from {agent_type.value} template",
            system_prompt=template["system_prompt"],
            capabilities=template["capabilities"],
            model="llama-3.3-70b-versatile",
            temperature=str(template["temperature"]),
            max_tokens=str(template["max_tokens"]),
            agent_metadata={"created_from": "template"}
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent
    
    @staticmethod
    def get_agent(db: Session, agent_id: UUID) -> Optional[Agent]:
        return db.query(Agent).filter(Agent.id == agent_id).first()
    
    @staticmethod
    def get_all_agents(db: Session, skip: int = 0, limit: int = 100, agent_type: Optional[AgentType] = None) -> List[Agent]:
        query = db.query(Agent)
        if agent_type:
            query = query.filter(Agent.agent_type == agent_type)
        return query.order_by(Agent.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_agent(db: Session, agent_id: UUID, agent_data: AgentUpdate) -> Optional[Agent]:
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return None
        
        update_data = agent_data.model_dump(exclude_unset=True)
        
        if "temperature" in update_data:
            update_data["temperature"] = str(update_data["temperature"])
        if "max_tokens" in update_data:
            update_data["max_tokens"] = str(update_data["max_tokens"])
        
        for key, value in update_data.items():
            setattr(agent, key, value)
        
        db.commit()
        db.refresh(agent)
        return agent
    
    @staticmethod
    def delete_agent(db: Session, agent_id: UUID) -> bool:
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return False
        db.delete(agent)
        db.commit()
        return True

agent_service = AgentService()
