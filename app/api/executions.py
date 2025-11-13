from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.schemas.execution import ExecutionCreate, ExecutionResponse
from app.services.execution_service import execution_service

router = APIRouter()

@router.post("/execute", response_model=ExecutionResponse, status_code=201)
async def execute_agent(
    execution_data: ExecutionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        execution = execution_service.create_execution(db, execution_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    background_tasks.add_task(execution_service.process_execution, db, execution.id)
    
    return execution

@router.get("/{execution_id}", response_model=ExecutionResponse)
def get_execution(execution_id: UUID, db: Session = Depends(get_db)):
    execution = execution_service.get_execution(db, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution

@router.get("/", response_model=List[ExecutionResponse])
def get_all_executions(
    skip: int = 0,
    limit: int = 100,
    agent_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    executions = execution_service.get_all_executions(db, skip, limit, agent_id)
    return executions

@router.delete("/{execution_id}")
def delete_execution(execution_id: UUID, db: Session = Depends(get_db)):
    success = execution_service.delete_execution(db, execution_id)
    if not success:
        raise HTTPException(status_code=404, detail="Execution not found")
    return {"message": "Execution deleted successfully", "execution_id": str(execution_id)}
