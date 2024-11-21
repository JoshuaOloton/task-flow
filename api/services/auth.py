from api.db.models import User
from api.db.database import get_db
from api.schemas.user import RegisterBase, TokenData, TokenPayload
from config import settings

from datetime import datetime, timedelta 
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
from utils.email import is_valid_email
from utils.hash import PasswordHasher
from typing import Annotated
import jwt
import re


ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES
ALGORITHM = settings.ALGORITHM
JWT_SECRET_KEY = settings.JWT_SECRET_KEY


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AuthService:
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()

        if expires_delta is not None:
            expires = datetime.now() + expires_delta
        else:
            expires = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expires, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict, expires_delta: timedelta | None):
        to_encode = data.copy()

        if expires_delta is not None:
            expires = datetime.now() + expires_delta
        else:
            expires = datetime.now() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expires, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt
    
    @staticmethod
    async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")

            if user_id is None:
                raise credentials_exception
            
            token_data = TokenData(id=user_id)

        except InvalidTokenError:
            raise credentials_exception
        
        user = db.query(User).filter(User.id == token_data.id).first()

        if user is None:
            raise credentials_exception
        
        return user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        if not is_valid_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid email address.'
            )
        
        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'User with email {email} not found.'
            )
        
        if not PasswordHasher.verify_password(user.password, password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Incorrect password.'
            )
        
        return user

    @staticmethod
    def create(db: Session, schema: RegisterBase):
        if not is_valid_email(schema.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid email address.'
            )
        

        user = db.query(User).filter(User.email == schema.email).first()

        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'User with email {schema.email} already exists.'
            )
        
        user = User(
            email=schema.email,
            username=schema.username,
            password=PasswordHasher.generate_hash(schema.password)
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def login(db: Session):
        pass