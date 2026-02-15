import logging
import sys
import os

# Ultra-early logging for Vercel troubleshooting
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger("vercel_main")
logger.info("Vercel Serverless Function (index.py) is starting at 06:15...")

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create a minimal app for heartbeats
app = FastAPI()

@app.get("/api/ping")
def ping():
    return {"status": "ok", "source": "direct_from_index_py", "timestamp": "06:15"}

@app.get("/api-test")
def api_test_direct():
    return {"status": "ok", "message": "Direct API Test from index.py is WORKING", "version": "v1.5.2"}

# Add project root to sys.path so app module is found
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Try to load the real application
try:
    logger.info("Attempting to import app.main...")
    from app.main import app as main_app
    # If successful, we want Vercel to use the real app
    app = main_app
    logger.info("Successfully loaded real app from app.main")
except Exception as e:
    logger.error(f"FATAL: Failed to import app.main: {e}", exc_info=True)
    import traceback
    
    @app.get("/{full_path:path}")
    def catch_all(full_path: str):
        return JSONResponse({
            "status": "error",
            "message": "EduNexia API failed to load",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "sys_path": sys.path
        }, status_code=500)
