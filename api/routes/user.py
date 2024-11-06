from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from api.db.database import get_db
from api.services.auth import AuthService
from api.services.user import UserService
from api.schemas.user import UserResponse, UserBase

user_router = APIRouter(prefix='/users', tags=['User'])

# POST /users/register
@user_router.post("/register", response_model=UserResponse)
def register_user(user: UserBase, db: Session = Depends(get_db)):
    user = AuthService.create(db, user)
    return user


# POST /users/login
@user_router.get("/{task_id}", response_model=UserResponse)
def login_user(task_id: str, db: Session = Depends(get_db)):
    pass
