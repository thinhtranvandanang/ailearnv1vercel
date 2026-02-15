import logging
import sys
import os

# Ultra-early logging for Vercel troubleshooting
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger("vercel_gateway")

# Add project root to sys.path so app module is found
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Placeholder app in case of fatal import error
from fastapi import FastAPI
from fastapi.responses import JSONResponse
app = FastAPI()

@app.get("/api/ping")
def ping():
    return {"status": "ok", "source": "index_py_gateway", "timestamp": "06:25"}

try:
    logger.info("Verifying environment and importing app.main...")
    from app.main import app as main_app
    # If successful, use the real app
    app = main_app
    logger.info("Successfully loaded real FastAPI app")
except Exception as e:
    logger.error(f"CRITICAL: Failed to load application: {e}", exc_info=True)
    import traceback
    
    @app.get("/{full_path:path}")
    def catch_all(full_path: str):
        return JSONResponse({
            "status": "error",
            "message": "EduNexia Backend failed to start",
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc().split("\n")[-3:], # Just the tip
            "tip": "Check if all dependencies in requirements.txt are installed."
        }, status_code=500)
