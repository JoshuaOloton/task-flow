from api.db.models import User
from api.schemas.user import UserBase
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from utils.hash import PasswordHasher

class AuthService:
    @staticmethod
    def create(db: Session, schema: UserBase):
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