from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from api.db.database import get_db
from api.db.models import User
from api.services.auth import AuthService
from api.schemas.user import UserResponse, LoginBase, RegisterBase, LoginResponse

user_router = APIRouter(prefix='/users', tags=['User'])

# POST /users/register
@user_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: RegisterBase, db: Session = Depends(get_db)):
    user = AuthService.create(db, user)

    return user


# POST /users/login
@user_router.post("/login", response_model=LoginResponse)
def login_user(user: LoginBase, db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, user.email, user.password)
    token = AuthService.create_access_token(data={"sub": str(user.id)})

    return LoginResponse (
        access_token=token,
        token_type="bearer",
        email=user.email,
        username=user.username
    )

# GET /users/me
@user_router.get("/me", response_model=UserResponse)
def get_user_me(current_user: User = Depends(AuthService.get_current_user)):
    return current_user
