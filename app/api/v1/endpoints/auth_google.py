"""Google OAuth login endpoints."""

import logging
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.services.auth_service import auth_service

logger = logging.getLogger(__name__)
router = APIRouter()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def get_google_login_url(redirect_uri: str) -> str:
    """Tạo URL redirect đến Google OAuth consent screen."""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


@router.get("/login")
async def google_login():
    """Redirect user to Google OAuth consent screen."""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=501,
            detail="Google OAuth chưa được cấu hình. Thêm GOOGLE_CLIENT_ID và GOOGLE_CLIENT_SECRET vào .env",
        )
    # Callback URL - backend nhận code từ Google
    redirect_uri = settings.GOOGLE_REDIRECT_URI or "http://localhost:8000/api/v1/auth/google/callback"
    url = get_google_login_url(redirect_uri)
    return RedirectResponse(url=url)


@router.get("/callback")
async def google_callback(
    code: str | None = None,
    error: str | None = None,
):
    """Xử lý callback từ Google, đổi code lấy token, tạo JWT, redirect về frontend."""
    if error:
        # User từ chối hoặc có lỗi
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error={error}",
            status_code=302,
        )
    if not code:
        raise HTTPException(status_code=400, detail="Không nhận được mã xác thực từ Google")

    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=501, detail="Google OAuth chưa được cấu hình")

    redirect_uri = settings.GOOGLE_REDIRECT_URI or "http://localhost:8000/api/v1/auth/google/callback"
    frontend_url = settings.FRONTEND_URL.rstrip("/")

    try:
        async with httpx.AsyncClient() as client:
            # Đổi code lấy access_token
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
                logger.warning(
                    "Google token exchange failed: status=%s body=%s",
                    token_resp.status_code,
                    token_resp.text[:500],
                )
                return RedirectResponse(
                    url=f"{frontend_url}/login?error=token_exchange_failed",
                    status_code=302,
                )
            tokens = token_resp.json()
            access_token_google = tokens.get("access_token")
            if not access_token_google:
                return RedirectResponse(
                    url=f"{frontend_url}/login?error=no_access_token",
                    status_code=302,
                )

            # Lấy thông tin user từ Google
            userinfo_resp = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token_google}"},
            )
            if userinfo_resp.status_code != 200:
                return RedirectResponse(
                    url=f"{frontend_url}/login?error=userinfo_failed",
                    status_code=302,
                )
            google_user = userinfo_resp.json()
            email = (google_user.get("email") or "").strip().lower()
            if not email:
                return RedirectResponse(
                    url=f"{frontend_url}/login?error=no_email",
                    status_code=302,
                )
            full_name = google_user.get("name", "") or email.split("@")[0]
            google_id = str(google_user.get("id", ""))

        # Dùng session mới sau khi await để tránh session/connection bị đóng
        db = SessionLocal()
        try:
            user = auth_service.get_or_create_google_user(
                db, email=email, full_name=full_name, google_id=google_id
            )
            jwt_token = create_access_token(subject=user.id)
            return RedirectResponse(
                url=f"{frontend_url}/auth/callback?token={jwt_token}",
                status_code=302,
            )
        finally:
            db.close()
    except Exception as e:
        logger.exception("Google OAuth callback error: %s", e)
        return RedirectResponse(
            url=f"{frontend_url}/login?error=callback_failed",
            status_code=302,
        )
