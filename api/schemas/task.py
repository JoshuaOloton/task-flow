from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date
from api.enums.task import PriorityLevel, TaskStatus
from uuid import UUID
from .shared import User

class TaskBase(BaseModel):
    title: str
    description: str
    dueDate: date
    status: TaskStatus
    priority: Optional[PriorityLevel] = None
    tags: Optional[List[str]] = []


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    description: str
    dueDate: date
    status: TaskStatus

    user: Optional[User] = None


class PaginatedTaskResponse(BaseModel):
    total: int
    skip: int
    limit: int
    tasks: List[TaskResponse]