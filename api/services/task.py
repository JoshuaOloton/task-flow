from api.db.models import Task, User
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
    def create(db: Session, schema: TaskBase, current_user: User | None = None):

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
        
        task.update(schema.model_dump())
        db.commit()
        return task.first()