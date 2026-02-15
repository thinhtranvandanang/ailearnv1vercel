import logging
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exceptions import EduNexiaException

# Configure logging to stdout so it appears in Vercel logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Configuration
# Đảm bảo Middleware này luôn chạy để chặn và xử lý preflight OPTIONS
# Nguyên tắc: allow_credentials=True KHÔNG ĐƯỢC dùng với allow_origins=["*"]
origins = [str(origin) for origin in settings.CORS_ORIGINS]
use_wildcard = not origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True if not use_wildcard else False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(EduNexiaException)
async def edunexia_exception_handler(request: Request, exc: EduNexiaException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail},
    )

# Routers
@app.get("/api/debug-auth")
def debug_auth():
    from app.core.config import settings
    import os
    return {
        "version": "v1.5.2-CONSOLIDATED-FIX",
        "google_client_id_set": bool(settings.GOOGLE_CLIENT_ID),
        "google_redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "frontend_url": settings.FRONTEND_URL,
        "api_v1_str": settings.API_V1_STR,
        "environment": os.environ.get("ENVIRONMENT", "not set")
    }

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "EduNexia API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)