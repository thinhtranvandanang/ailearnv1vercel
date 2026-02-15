import logging
import sys
import os

# Ultra-early logging for Vercel troubleshooting
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger("vercel_main")
logger.info("Vercel Serverless Function (index.py) is starting at 06:00...")

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
