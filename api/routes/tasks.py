from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from api.db.database import get_db
from api.db.models import User
from api.services.auth import AuthService
from api.services.task import TaskService
from api.schemas.task import TaskResponse, TaskBase

task_router = APIRouter(prefix='/tasks', tags=['Task'])

# GET /tasks
@task_router.get("/", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return TaskService.get_all_tasks(db)


# GET /tasks/{task_id}
@task_router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    return TaskService.get_task_by_id(db, task_id)


# POST /tasks
@task_router.post("/", response_model=TaskResponse)
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