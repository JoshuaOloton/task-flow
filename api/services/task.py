from api.db.models import Task, User
from api.schemas.task import PaginatedTaskResponse
from api.schemas.task import TaskBase
from cache import redis_cache
from config import settings
from utils.validators import is_valid_uuid

import json
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError



REDIS_SHORT_TTL = settings.REDIS_SHORT_TTL


class TaskService:

    @staticmethod
    def invalidate_task_pagination_cache():
        # invalidate all task pagination cache
        print('Invalidating task pagination cache...')
        cache_key = 'tasks:*:skip:*:limit:*:status:*:priority:*'
        count_cache_key = 'total_tasks:*:status:*:priority:*'

        for key in redis_cache.scan_iter(cache_key):
            redis_cache.delete(key)

        for key in redis_cache.scan_iter(count_cache_key):
            redis_cache.delete(key)

    @staticmethod
    def get_task_by_id(db: Session, task_id: str, current_user: User):
        # validate task_id
        task_id = task_id.strip()

        if not is_valid_uuid(task_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid task id. Task id must be a valid UUID.'
            )

        # fetch task from cache
        task = redis_cache.get(f'task:{current_user.id}:{task_id}')
        if task:
            print('Task cache hit')
            return json.loads(task)

        print('Task cache miss, fetching from db...')

        task = db.query(Task).filter(
            and_(
                Task.id == task_id,
                Task.created_by == current_user.id
            )
        ).first()

        if not task:
            print('Task not found')
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Task with id {task_id} not found.'
            )
        
        # cache task
        redis_cache.setex(f'task:{current_user.id}:{task_id}', REDIS_SHORT_TTL, json.dumps(task.to_dict()))
        return task


    @staticmethod
    def get_tasks_paginated(db: Session, current_user: User, skip: int, limit: int, status_query: str = None, priority: str = None):

        try:
            # fetch tasks from cache
            cache_key = f'tasks:{current_user.id}:skip:{skip}:limit:{limit}:status:{status_query or "None"}:priority:{priority or "None"}'
            count_cache_key = f'total_tasks:{current_user.id}:status:{status_query or "None"}:priority:{priority or "None"}'

            tasks = redis_cache.get(cache_key)
            total_tasks = redis_cache.get(count_cache_key)
            
            if tasks and total_tasks:
                tasks = json.loads(tasks)
                total_tasks = int(total_tasks)
                print('Task cache hit')
            else:
                print('Task cache miss, fetching from db...')

                tasks = db.query(Task).filter(Task.created_by == current_user.id)

                # filter tasks by status and priority
                if status_query:
                    tasks = tasks.filter(Task.status == status_query)
                if priority:
                    tasks = tasks.filter(Task.priority == priority)

                 # Get the total number of tasks
                total_tasks = tasks.count() 

                tasks = tasks.offset(skip).limit(limit).all()

                # cache tasks and total_tasks
                redis_cache.setex(cache_key, REDIS_SHORT_TTL, json.dumps([task.to_dict() for task in tasks]))
                redis_cache.setex(count_cache_key, REDIS_SHORT_TTL, total_tasks)

            return PaginatedTaskResponse(
                total=total_tasks,
                skip=skip,
                limit=limit,
                tasks=tasks
            )
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'An error occurred while fetching tasks: {str(e)}'
            )

    
    @staticmethod
    def create(db: Session, schema: TaskBase, current_user: User):
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

            redis_cache.setex(f'task:{current_user.id}:{task.id}', REDIS_SHORT_TTL, json.dumps(task.to_dict()))

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
                detail=f'An unexpected error occurred while creating the task: {str(e)}'
            )
        
    
    @staticmethod
    def delete(db: Session, task_id: str, current_user: User):
        # validate task_id
        task_id = task_id.strip()

        if not is_valid_uuid(task_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid task id. Task id must be a valid UUID.'
            )

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

            # delete from cache 
            redis_cache.delete(f'task:{current_user.id}:{task_id}')

            TaskService.invalidate_task_pagination_cache()

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='An error occurred while deleting the task.'
            )


    @staticmethod
    def put_update(db: Session, task_id: str, schema: TaskBase, current_user: User):
        # validate task_id
        task_id = task_id.strip()

        if not is_valid_uuid(task_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid task id. Task id must be a valid UUID.'
            )

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
            redis_cache.setex(f'task:{current_user.id}:{task_id}', REDIS_SHORT_TTL, json.dumps(task.first().to_dict()))

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
        

    @staticmethod
    def patch_update(db: Session, task_id: str, schema: TaskBase, current_user: User):
        # validate task_id
        task_id = task_id.strip()

        if not is_valid_uuid(task_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid task id. Task id must be a valid UUID.'
            )

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
            
            # ensure at least one field is provided in request body and update only provided task fields
            if not any([value for key, value in schema.model_dump().items() if value]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='At least one field is required to update the task.'
                )

            for key, value in schema.model_dump().items():
                setattr(task.first(), key, value)

            # update cache
            redis_cache.setex(f'task:{current_user.id}:{task_id}', REDIS_SHORT_TTL, json.dumps(task.first().to_dict()))

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