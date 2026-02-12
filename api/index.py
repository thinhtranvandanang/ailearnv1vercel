from fastapi import FastAPI
from fastapi.responses import JSONResponse

# This is the entry point for Vercel Serverless Functions
try:
    from app.main import app
except Exception as e:
    import traceback
    app = FastAPI()
    
    @app.get("/{full_path:path}")
    def catch_all(full_path: str):
        return JSONResponse({
            "status": "error",
            "message": "EduNexia API failed to load",
            "error": str(e),
            "traceback": traceback.format_exc()
        }, status_code=500)
