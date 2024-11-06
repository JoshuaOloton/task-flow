from api.db.models import Task
from sqlalchemy.orm import Session
from api.schemas.task import TaskBase
from fastapi import HTTPException, status


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
    def create(db: Session, schema: TaskBase):
        task = Task(**schema.model_dump())
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def delete(db: Session, task_id: str):
        task = db.query(Task).get(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Task with id {task_id} not found.'
            )
        
        db.delete(task)
        db.commit()
        return 'OK'

    @staticmethod
    def update(db: Session, task_id: str, schema: TaskBase):
        task = db.query(Task).filter(Task.id == task_id)
        if not task.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Task with id {task_id} not found.'
            )
        
        task.update(schema.model_dump())
        db.commit()
        return 'OK'