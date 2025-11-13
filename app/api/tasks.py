from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.schemas.task import TaskCreate, TaskResponse
from app.services.task_service import task_service

router = APIRouter()

@router.post("/create", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    task = task_service.create_task(db, task_data)
    
    background_tasks.add_task(task_service.process_task, db, task.id)
    
    return task


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: UUID, db: Session = Depends(get_db)):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/{task_id}/result")
def get_task_result(task_id: UUID, db: Session = Depends(get_db)):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": str(task.id),
        "status": task.status,
        "result": task.result,
        "error": task.error
    }

@router.get("/", response_model=List[TaskResponse])
def get_all_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = task_service.get_all_tasks(db, skip, limit)
    return tasks
