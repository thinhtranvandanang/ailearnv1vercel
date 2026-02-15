"""Google OAuth login endpoints."""

import logging
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.services.auth_service import auth_service

logger = logging.getLogger(__name__)
router = APIRouter()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def get_dynamic_config(request: Request):
    """Tính toán URL linh hoạt dựa trên request thực tế để hỗ trợ Production/Local."""
    # Môi trường Vercel/Proxy cung cấp x-forwarded-* headers
    forwarded_host = request.headers.get("x-forwarded-host")
    forwarded_proto = request.headers.get("x-forwarded-proto")
    
    current_host = forwarded_host or request.url.netloc
    is_localhost = "localhost" in current_host
    
    # Ép buộc HTTPS trên Production (không phải localhost)
    if is_localhost:
        protocol = request.url.scheme
    else:
        # Vercel luôn có x-forwarded-proto=https. Nếu không có, mặc định là https.
        protocol = forwarded_proto or "https"
    
    base_url = f"{protocol}://{current_host}"
    
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


@router.get("/google/login")
async def google_login(request: Request):
    """Redirect user to Google OAuth consent screen."""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=501,
            detail="Google OAuth chưa được cấu hình. Thêm GOOGLE_CLIENT_ID và GOOGLE_CLIENT_SECRET vào .env",
        )
    
    _, redirect_uri = get_dynamic_config(request)
    logger.info(f"Initiating Google login with redirect_uri: {redirect_uri}")
    
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url=url)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str | None = None,
    error: str | None = None,
):
    """Xử lý callback từ Google, đổi code lấy token, tạo JWT, redirect về frontend."""
    frontend_url, redirect_uri = get_dynamic_config(request)
    
    if error:
        # User từ chối hoặc có lỗi
        logger.error(f"Google OAuth Provider Error: {error}")
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?error=access_denied&details={error}",
            status_code=302,
        )
    if not code:
        logger.warning("Google callback hit without code or error")
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?error=missing_code",
            status_code=302,
        )

    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=501, detail="Google OAuth chưa được cấu hình")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # 1. Trao đổi mã lấy token từ Google
            token_resp = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if token_resp.status_code != 200:
                logger.error(
                    f"Google token exchange failed (Redirect URI: {redirect_uri}): {token_resp.text[:500]}"
                )
                return RedirectResponse(
                    url=f"{frontend_url}/auth/callback?error=token_failed&status={token_resp.status_code}",
                    status_code=302,
                )
            
            tokens = token_resp.json()
            access_token_google = tokens.get("access_token")
            if not access_token_google:
                return RedirectResponse(
                    url=f"{frontend_url}/auth/callback?error=no_access_token",
                    status_code=302,
                )

            # 2. Lấy thông tin người dùng (UserInfo)
            userinfo_resp = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token_google}"},
            )
            if userinfo_resp.status_code != 200:
                logger.error(f"Google UserInfo fetch failed: {userinfo_resp.text[:500]}")
                return RedirectResponse(
                    url=f"{frontend_url}/auth/callback?error=user_info_failed",
                    status_code=302,
                )
            
            google_user = userinfo_resp.json()
            email = (google_user.get("email") or "").strip().lower()
            if not email:
                logger.error("Google profile missing email")
                return RedirectResponse(
                    url=f"{frontend_url}/auth/callback?error=email_missing",
                    status_code=302,
                )
            
            full_name = google_user.get("name", "") or email.split("@")[0]
            google_id = str(google_user.get("id") or google_user.get("sub", ""))

        # 3. Tạo một Database Session mới ngay sau khi thực hiện các lệnh await
        db = SessionLocal()
        try:
            user = auth_service.get_or_create_google_user(
                db, email=email, full_name=full_name, google_id=google_id
            )
            jwt_token = create_access_token(subject=user.id)
            logger.info(f"Google login successful for: {email}")
            # Redirect về Frontend kèm Token JWT
            return RedirectResponse(
                url=f"{frontend_url}/auth/callback?token={jwt_token}",
                status_code=302,
            )
        except Exception as db_e:
            err_msg = str(db_e)
            logger.exception(f"Database error during Google callback for {email}")
            db.rollback()
            # Trả thêm chi tiết lỗi để chẩn đoán trên Frontend
            params = {
                "error": "callback_failed",
                "details": "db_error",
                "message": err_msg[:200]
            }
            return RedirectResponse(
                url=f"{frontend_url}/auth/callback?{urlencode(params)}",
                status_code=302,
            )
        finally:
            db.close()
    except Exception as e:
        logger.exception("Unexpected exception in Google callback flow")
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?error=callback_failed&details=exception",
            status_code=302,
        )
