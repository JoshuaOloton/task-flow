from pydantic import BaseModel, ConfigDict
from datetime import date


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str
    username: str
    password: str

class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    title: str
    description: str
    dueDate: date
    status: str
