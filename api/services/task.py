from api.db.models import Task, User
from api.schemas.task import PaginatedTaskResponse
from api.schemas.task import TaskBase
from cache import redis_cache
from config import settings

from datetime import date
from fastapi import HTTPException, status
import json
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError



REDIS_SHORT_TTL = settings.REDIS_SHORT_TTL
REDIS_MEDIUM_TTL = settings.REDIS_MEDIUM_TTL


class TaskService:

    @staticmethod
    def invalidate_task_pagination_cache():
        # invalidate all task pagination cache
        print('Invalidating task pagination cache...')
        for key in redis_cache.scan_iter('tasks:*:*'):
            redis_cache.delete(key)

    @staticmethod
    def get_task_by_id(db: Session, task_id: str):
        # trim task_id
        task_id = task_id.strip()

        try:
            # fetch task from cache
            task = redis_cache.get(f'task:{task_id}')
            if task:
                print('Task cache hit')
                return json.loads(task)

            print('Task cache miss, fetching from db...')
            task = db.query(Task).get(task_id)
            if not task:
                print('Task not found')
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Task with id {task_id} not found.'
                )
            
            # cache task
            redis_cache.setex(f'task:{task_id}', REDIS_SHORT_TTL, json.dumps(task.to_dict()))
            return task
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='An error occurred while fetching the task.'
            )


    # @staticmethod
    # def get_all_tasks(db: Session):
    #     # fetch tasks from cache
    #     tasks = redis_cache.get('tasks')
    #     if tasks:
    #         return json.loads(tasks)
                              
    #     tasks = db.query(Task).all()
    #     # cache tasks
    #     redis_cache.setex('tasks', REDIS_TTL, json.dumps([task.to_dict() for task in tasks]))
    #     return tasks

    @staticmethod
    def get_tasks_paginated(db: Session, skip: int, limit: int):

        try:
            # fetch tasks from cache
            tasks = redis_cache.get(f'tasks:{skip}:{limit}')
            total_tasks = redis_cache.get('total_tasks')
            
            if tasks and total_tasks:
                tasks = json.loads(tasks)
                total_tasks = int(total_tasks)
                print('Task cache hit')
            else:
                print('Task cache miss, fetching from db...')
                tasks = db.query(Task).offset(skip).limit(limit).all()
                total_tasks = db.query(Task).count()  # Get the total number of tasks

                # cache tasks and total_tasks
                redis_cache.setex(f'tasks:{skip}:{limit}', REDIS_SHORT_TTL, json.dumps([task.to_dict() for task in tasks]))
                redis_cache.setex('total_tasks', REDIS_MEDIUM_TTL, total_tasks)

            return PaginatedTaskResponse(
                total=total_tasks,
                skip=skip,
                limit=limit,
                tasks=tasks
            )
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='An error occurred while fetching tasks.'
            )

    
    @staticmethod
    def create(db: Session, schema: TaskBase, current_user: User | None = None):
        # confirm date is not in the past
        if schema.dueDate < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Due date cannot be in the past.'
            )
        
        try:
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

            redis_cache.setex(f'task:{task.id}', REDIS_SHORT_TTL, json.dumps(task.to_dict()))

            # increment cache total tasks
            if not redis_cache.get('total_tasks'):
                total = db.query(Task).count()
                redis_cache.setex('total_tasks', REDIS_MEDIUM_TTL, total)
            else:
                redis_cache.incr('total_tasks')

            # invalidate all task pagination cache
            TaskService.invalidate_task_pagination_cache()

            return task
        
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='An error occurred while creating the task.'
            )
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='An unexpected error occurred while creating the task.'
            )
        
    
    @staticmethod
    def delete(db: Session, task_id: str, current_user: User):
        # trim task_id
        task_id = task_id.strip()

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

            # delete from cache and decrement total tasks
            redis_cache.delete(f'task:{task_id}')
            if not redis_cache.get('total_tasks'):
                total = db.query(Task).count()
                redis_cache.setex('total_tasks', REDIS_MEDIUM_TTL, total)
            else:
                redis_cache.decr('total_tasks')

            # invalidate all task pagination cache
            TaskService.invalidate_task_pagination_cache()

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='An error occurred while deleting the task.'
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='An unexpected error occurred while deleting the task.'
            )

    @staticmethod
    def update(db: Session, task_id: str, schema: TaskBase, current_user: User):
        # trim task_id
        task_id = task_id.strip()

        try:
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

            # update cache
            redis_cache.setex(f'task:{task_id}', REDIS_SHORT_TTL, json.dumps(task.first().to_dict()))

            # invalidate all task pagination cache
            TaskService.invalidate_task_pagination_cache()

            db.commit()
            return task.first()
        
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='An error occurred while updating the task.'
            )
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='An unexpected error occurred while updating the task.'
            )