from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.task import Task, TaskStatus
from app.models.agent import Agent
from app.schemas.task import TaskCreate
from app.agents.factory import agent_factory
from app.core.redis_client import redis_client

class TaskService:
    @staticmethod
    def create_task(db: Session, task_data: TaskCreate, user_id: str) -> Task:
        task = Task(
            user_id=user_id,
            description=task_data.description,
            status=TaskStatus.PENDING,
            task_metadata=task_data.task_metadata
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    async def process_task(db: Session, task_id: UUID):
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return
        
        try:
            task.status = TaskStatus.PROCESSING
            db.commit()
            
            await redis_client.set(f"task:{task_id}:status", "processing", expire=3600)
            
            agent_config = agent_factory.create_agent_config(task.description)
            
            agent_data = agent_factory.build_agent_from_config(agent_config, task.description)
            
            agent = Agent(
                user_id=task.user_id,
                name=agent_data["name"],
                agent_type=agent_data["agent_type"],
                description=agent_data["description"],
                system_prompt=agent_data["system_prompt"],
                capabilities=agent_data["capabilities"],
                model=agent_data["model"],
                temperature=str(agent_data["temperature"]),
                max_tokens=str(agent_data["max_tokens"]),
                agent_metadata=agent_data["agent_metadata"]
            )
            
            db.add(agent)
            db.commit()
            db.refresh(agent)
            
            result_output = agent_factory.execute_with_agent(agent, task.description)
            
            task.created_agent_id = agent.id
            task.status = TaskStatus.COMPLETED
            task.result = {
                "agent_id": str(agent.id),
                "agent_name": agent.name,
                "agent_type": agent.agent_type.value,
                "output": result_output,
                "config": agent_config
            }
            task.updated_at = datetime.utcnow()
            
            db.commit()
            
            await redis_client.set(f"task:{task_id}:status", "completed", expire=3600)
            await redis_client.set(f"task:{task_id}:result", task.result, expire=3600)
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.updated_at = datetime.utcnow()
            db.commit()
            
            await redis_client.set(f"task:{task_id}:status", "failed", expire=3600)
            await redis_client.set(f"task:{task_id}:error", str(e), expire=3600)
    
    @staticmethod
    def get_task(db: Session, task_id: UUID, user_id: str) -> Optional[Task]:
        return db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    
    @staticmethod
    def get_all_tasks(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Task]:
        return db.query(Task).filter(Task.user_id == user_id).order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete_task(db: Session, task_id: UUID, user_id: str) -> bool:
        task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
        if not task:
            return False
        db.delete(task)
        db.commit()
        return True

task_service = TaskService()