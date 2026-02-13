import logging
import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.auth import LoginRequest, Token, UserCreate, UserOut
from app.services.auth_service import auth_service
from app.core.response import APIResponse
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.account import User

logger = logging.getLogger(__name__)

router = APIRouter()
google_router = APIRouter()

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

def get_dynamic_config(request: Request):
    """Tính toán URL linh hoạt dựa trên request thực tế để hỗ trợ Production/Local."""
    # Ưu tiên x-forwarded-proto cho môi trường có proxy như Vercel
    is_localhost = "localhost" in request.url.netloc
    
    # Ép buộc HTTPS trên Production (không phải localhost) để tránh mất token do redirect HTTP -> HTTPS
    if is_localhost:
        protocol = request.url.scheme
    else:
        # Vercel luôn hỗ trợ HTTPS, x-forwarded-proto là đáng tin cậy nhất
        protocol = request.headers.get("x-forwarded-proto") or "https"
    
    base_url = f"{protocol}://{request.url.netloc}"
    
    # 1. Frontend URL
    frontend_url = settings.FRONTEND_URL.rstrip("/")
    if "localhost" in frontend_url or not frontend_url:
        frontend_url = base_url

    # 2. Google Redirect URI
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    if not redirect_uri or "localhost" in redirect_uri:
        # Đường dẫn callback định nghĩa qua api_router /auth/google/callback
        # api_router prefix = /api/v1 (settings.API_V1_STR)
        redirect_uri = f"{base_url}{settings.API_V1_STR}/auth/google/callback"
        
    return frontend_url, redirect_uri

@google_router.get("/google/login")
def google_login(request: Request):
    _, redirect_uri = get_dynamic_config(request)
    
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account"
    }
    query_params = "&".join([f"{k}={v}" for k, v in params.items()])
    return RedirectResponse(f"{base_url}?{query_params}")

@google_router.get("/google/callback")
async def google_callback(request: Request, code: str, error: str | None = None):
    frontend_url, redirect_uri = get_dynamic_config(request)
    
    if error:
        logger.error(f"Google OAuth Provider Error: {error}")
        return RedirectResponse(f"{frontend_url}/login?error=access_denied&details={error}")

    if not code:
        return RedirectResponse(f"{frontend_url}/login?error=missing_code")

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            # 1. Trao đổi mã lấy token từ Google
            token_resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                }
            )
            
            if token_resp.status_code != 200:
                err_text = token_resp.text
                logger.error(f"Google Token Exchange Failed (Redirect URI used: {redirect_uri}): {err_text}")
                return RedirectResponse(f"{frontend_url}/login?error=token_failed&status={token_resp.status_code}")
            
            token_data = token_resp.json()
            access_token = token_data.get("access_token")

            # 2. Lấy thông tin người dùng (UserInfo)
            userinfo_resp = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if userinfo_resp.status_code != 200:
                logger.error(f"Google UserInfo Fetch Failed: {userinfo_resp.text}")
                return RedirectResponse(f"{frontend_url}/login?error=user_info_failed")
                
            profile = userinfo_resp.json()
            email = (profile.get("email") or "").strip().lower()
            full_name = profile.get("name") or profile.get("given_name")
            google_id = str(profile.get("sub", ""))

            if not email:
                logger.error("Google profile missing email")
                return RedirectResponse(f"{frontend_url}/login?error=email_missing")

            # 3. Tạo một Database Session mới ngay sau khi thực hiện các lệnh await
            db = SessionLocal()
            try:
                user = auth_service.get_or_create_google_user(
                    db, 
                    email=email, 
                    full_name=full_name, 
                    google_id=google_id
                )
                jwt_token = create_access_token(subject=user.id)
                logger.info(f"Google login successful for: {email}")
                # Redirect về Frontend kèm Token JWT
                return RedirectResponse(f"{frontend_url}/login?token={jwt_token}")
            except Exception as db_e:
                logger.exception(f"Database error during Google callback for {email}")
                db.rollback()
                return RedirectResponse(f"{frontend_url}/login?error=callback_failed&details=db_error")
            finally:
                db.close()

        except Exception as e:
            logger.exception("Unexpected exception in Google callback flow")
            return RedirectResponse(f"{frontend_url}/login?error=callback_failed&details=exception")