from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List
from api.db.database import get_db
from api.db.models import User
from api.services.auth import AuthService
from api.services.task import TaskService
from api.schemas.task import TaskResponse, TaskBase, PaginatedTaskResponse


task_router = APIRouter(prefix='/tasks', tags=['Task'])


# GET /tasks with pagination
@task_router.get("/", response_model=PaginatedTaskResponse)
def get_tasks_paginated(
    skip: int = Query(0, ge=0), 
    limit: int = Query(10, ge=0, le=100), 
    status: str = Query(None),
    priority: str = Query(None),
    db: Session = Depends(get_db)
):
    
    return TaskService.get_tasks_paginated(db, skip=skip, limit=limit, status_query=status, priority=priority)


# GET /tasks/{task_id}
@task_router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    return TaskService.get_task_by_id(db, task_id)


# POST /tasks
@task_router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskBase, db: Session = Depends(get_db), current_user: User = Depends(AuthService.get_current_user)):
    task = TaskService.create(db, task, current_user)
    return task


# DELETE /tasks/{task_id}
@task_router.delete("/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db), current_user: User = Depends(AuthService.get_current_user)):
    
    TaskService.delete(db, task_id, current_user)
    return {
        "message": "Task deleted successfully."
    }


# PUT /tasks/{task_id}
@task_router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    task: TaskBase, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(AuthService.get_current_user)
):
    return TaskService.update(db, task_id, task, current_user)