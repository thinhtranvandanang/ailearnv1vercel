from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pkg_resources

# This is the entry point for Vercel Serverless Functions
try:
    from app.main import app
except Exception as e:
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
