
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.account import User
from app.core.exceptions import AuthException

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/student/login")

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            import logging
            logging.error("JWT Payload missing 'sub' claim")
            raise AuthException()
    except JWTError as e:
        import logging
        logging.error(f"JWT Decode Error: {str(e)}")
        raise AuthException()
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        import logging
        logging.error(f"User not found for ID: {user_id}")
        raise AuthException("User not found")
    if not user.is_active:
        import logging
        logging.error(f"User account is inactive for ID: {user_id}")
        raise AuthException("User account is inactive")
    return user

def get_current_student(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return current_user
