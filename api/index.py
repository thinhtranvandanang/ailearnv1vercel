from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Simple health check app that doesn't require database
app = FastAPI(title="EduNexia Health Check")

@app.get("/")
@app.get("/api")
@app.get("/api/v1")
def health_check():
    return JSONResponse({
        "status": "ok",
        "message": "Serverless function is running",
        "service": "EduNexia API"
    })

@app.get("/api/v1/health")
def detailed_health():
    import os
    return JSONResponse({
        "status": "ok",
        "environment": os.environ.get("VERCEL_ENV", "unknown"),
        "has_database_url": bool(os.environ.get("DATABASE_URL")),
        "python_version": os.sys.version
    })

# Try to import the main app, but fall back to health check if it fails
try:
    from app.main import app as main_app
    app = main_app
    print("✅ Successfully loaded main app")
except Exception as e:
    print(f"⚠️ Failed to load main app: {e}")
    print("Using health check app instead")
