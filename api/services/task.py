from api.db.models import Task, User
from api.schemas.task import PaginatedTaskResponse
from sqlalchemy.orm import Session
from api.schemas.task import TaskBase
from fastapi import HTTPException, status
from datetime import date


class TaskService:
    @staticmethod
    def get_task_by_id(db: Session, task_id: str):
        task = db.query(Task).get(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Task with id {task_id} not found.'
            )
        return task
    
    @staticmethod
    def get_all_tasks(db: Session):
        return db.query(Task).all()

    @staticmethod
    def get_tasks_paginated(db: Session, skip: int, limit: int):
        total_tasks = db.query(Task).count()    # Get the total number of tasks
        tasks = db.query(Task).offset(skip).limit(limit).all()

        return PaginatedTaskResponse(
            total=total_tasks,
            skip=skip,
            limit=limit,
            tasks=tasks
        )

    
    @staticmethod
    def create(db: Session, schema: TaskBase, current_user: User | None = None):
        # confirm date is not in the past
        if schema.dueDate < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Due date cannot be in the past.'
            )

        task = Task(
            title=schema.title,
            description=schema.description,
            dueDate=schema.dueDate,
            status=schema.status,
            priority=schema.priority,
            tags=schema.tags,
            created_by=current_user.id,
            assigned_to=current_user.email
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def delete(db: Session, task_id: str, current_user: User):
        try:
            task = db.query(Task).get(task_id)
            if not task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Task with id {task_id} not found.'
                )
            
            # check if current user id matches task user id
            if task.created_by and task.created_by != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='You are not authorized to delete this task.'
                )

            db.delete(task)
            db.commit()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='An error occurred while deleting the task.'
            )

    @staticmethod
    def update(db: Session, task_id: str, schema: TaskBase, current_user: User):
        task = db.query(Task).filter(Task.id == task_id)
        if not task.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Task with id {task_id} not found.'
            )
        
        # check if current user id matches task user id
        if task.first().created_by and task.first().created_by  != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You are not authorized to update this task.'
            )
        
        # confirm date is not in the past
        if schema.dueDate < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Due date cannot be in the past.'
            )
        
        task.update(schema.model_dump())
        db.commit()
        return task.first()