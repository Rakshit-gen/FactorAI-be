from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import time

from app.models.execution import Execution, ExecutionStatus
from app.models.agent import Agent
from app.schemas.execution import ExecutionCreate
from app.agents.factory import agent_factory
from app.core.redis_client import redis_client

class ExecutionService:
    @staticmethod
    def create_execution(db: Session, execution_data: ExecutionCreate) -> Execution:
        agent = db.query(Agent).filter(Agent.id == execution_data.agent_id).first()
        if not agent:
            raise ValueError(f"Agent with id {execution_data.agent_id} not found")
        
        execution = Execution(
            agent_id=execution_data.agent_id,
            input_data=execution_data.input_data,
            status=ExecutionStatus.PENDING,
            execution_metadata=execution_data.execution_metadata
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        return execution
    
    @staticmethod
    async def process_execution(db: Session, execution_id: UUID):
        execution = db.query(Execution).filter(Execution.id == execution_id).first()
        if not execution:
            return
        
        try:
            execution.status = ExecutionStatus.RUNNING
            db.commit()
            
            await redis_client.set(f"execution:{execution_id}:status", "running", expire=3600)
            
            agent = db.query(Agent).filter(Agent.id == execution.agent_id).first()
            if not agent:
                raise ValueError(f"Agent not found")
            
            start_time = time.time()
            
            output = agent_factory.execute_with_agent(agent, execution.input_data)
            
            end_time = time.time()
            execution_time = f"{end_time - start_time:.2f}s"
            
            execution.status = ExecutionStatus.COMPLETED
            execution.output = output
            execution.execution_time = execution_time
            execution.completed_at = datetime.utcnow()
            
            db.commit()
            
            await redis_client.set(f"execution:{execution_id}:status", "completed", expire=3600)
            await redis_client.set(f"execution:{execution_id}:output", output, expire=3600)
            
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)
            execution.completed_at = datetime.utcnow()
            db.commit()
            
            await redis_client.set(f"execution:{execution_id}:status", "failed", expire=3600)
            await redis_client.set(f"execution:{execution_id}:error", str(e), expire=3600)
    
    @staticmethod
    def get_execution(db: Session, execution_id: UUID) -> Optional[Execution]:
        return db.query(Execution).filter(Execution.id == execution_id).first()
    
    @staticmethod
    def get_all_executions(db: Session, skip: int = 0, limit: int = 100, agent_id: Optional[UUID] = None) -> List[Execution]:
        query = db.query(Execution)
        if agent_id:
            query = query.filter(Execution.agent_id == agent_id)
        return query.order_by(Execution.created_at.desc()).offset(skip).limit(limit).all()

execution_service = ExecutionService()
