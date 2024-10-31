from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from .shared import User, Task

class UserBase(BaseModel):
    email: str
    username: str
    password: str

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    email: str
    username: str
    tasks: List[Task] = []