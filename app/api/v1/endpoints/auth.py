import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.auth import LoginRequest, UserCreate, UserOut
from app.services.auth_service import auth_service
from app.core.response import APIResponse
from app.models.account import User

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login")
def login(request_data: LoginRequest, db: Session = Depends(deps.get_db)):
    result = auth_service.authenticate_student(
        db, 
        username=request_data.username, 
        password=request_data.password
    )
    return APIResponse.success(data=result)

@router.post("/register")
def register(user_in: UserCreate, db: Session = Depends(deps.get_db)):
    result = auth_service.register_student(db, user_in=user_in)
    return APIResponse.success(data=result, message="Đăng ký tài khoản thành công")

@router.get("/me", response_model=APIResponse[UserOut])
def get_me(current_user: User = Depends(deps.get_current_user)):
    return APIResponse.success(data=current_user)