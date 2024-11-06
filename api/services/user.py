from api.db.models import User
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

class UserService:
    @staticmethod
    def get_user_by_email(db: Session, email: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'User with email {email} not found.'
            )
        return user
    
    
