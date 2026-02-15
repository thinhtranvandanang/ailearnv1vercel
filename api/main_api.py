import logging
import sys
import os

# Ultra-early logging for Vercel troubleshooting
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger("vercel_main")
logger.info("Vercel Serverless Function (main_api.py) is starting...")

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pkg_resources

# This is the entry point for Vercel Serverless Functions
try:
    logger.info("Attempting to import app.main...")
    from app.main import app
except Exception as e:
    logger.error(f"FATAL: Failed to import app.main: {e}", exc_info=True)
    import traceback
    import sys
    app = FastAPI()
    
    installed_packages = [f"{d.project_name}=={d.version}" for d in pkg_resources.working_set]
    
    @app.get("/debug-auth")
    def debug_auth():
        from app.core.config import settings
        return {
            "version": "v1.5.2-CONSOLIDATED-FIX",
            "google_client_id_set": bool(settings.GOOGLE_CLIENT_ID),
            "google_redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "frontend_url": settings.FRONTEND_URL,
            "api_v1_str": settings.API_V1_STR,
            "environment": os.environ.get("ENVIRONMENT", "not set")
        }

    @app.get("/{full_path:path}")
    def catch_all(full_path: str):
        return JSONResponse({
            "status": "error",
            "message": "EduNexia API failed to load",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "installed_packages": installed_packages,
            "sys_path": sys.path
        }, status_code=500)
