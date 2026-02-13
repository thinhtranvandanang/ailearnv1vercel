from typing import List, Union, Optional, Any
from pydantic import AnyHttpUrl, validator, root_validator, BaseSettings, Field

class EduNexiaSettings(BaseSettings):
    PROJECT_NAME: str = "EduNexia API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "development_secret_key_change_me_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/edunexia"

    @validator("DATABASE_URL", pre=True)
    @classmethod
    def assemble_db_url(cls, v: str) -> str:
        if isinstance(v, str):
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql://", 1)
            elif v.startswith("postgresql+psycopg://"):
                return v.replace("postgresql+psycopg://", "postgresql://", 1)
        return v

    # CORS
    # Đổi tên hoàn toàn để Pydantic V1 không bao giờ nhầm lẫn
    CORS_ORIGINS: List[str] = []
    ALLOWED_ORIGINS: Optional[str] = None

    @root_validator(pre=True)
    def manual_load_env_vars(cls, values):
        import os
        import json
        
        # Manual load BACKEND_CORS_ORIGINS
        raw_cors = os.environ.get("BACKEND_CORS_ORIGINS")
        if raw_cors:
            if raw_cors.startswith("["):
                try:
                    values["CORS_ORIGINS"] = json.loads(raw_cors)
                except:
                    values["CORS_ORIGINS"] = [i.strip() for i in raw_cors.split(",") if i.strip()]
            else:
                 values["CORS_ORIGINS"] = [i.strip() for i in raw_cors.split(",") if i.strip()]
        
        # Manual load FILE_EXTENSIONS
        raw_ext = os.environ.get("ALLOWED_FILE_EXTENSIONS")
        if raw_ext:
            if raw_ext.startswith("["):
                try:
                    values["FILE_EXTENSIONS"] = json.loads(raw_ext)
                except:
                    values["FILE_EXTENSIONS"] = [i.strip() for i in raw_ext.split(",") if i.strip()]
            else:
                values["FILE_EXTENSIONS"] = [i.strip() for i in raw_ext.split(",") if i.strip()]

        # Force load critical security & OAuth variables for Vercel compatibility
        for key in ["SECRET_KEY", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REDIRECT_URI", "FRONTEND_URL"]:
            env_val = os.environ.get(key)
            if env_val:
                values[key] = env_val

        return values
    
    @root_validator
    def sync_cors_origins_logic(cls, values):
        """Nếu có ALLOWED_ORIGINS trong .env, nạp vào CORS_ORIGINS."""
        allowed_origins = values.get("ALLOWED_ORIGINS")
        backend_cors_origins = values.get("CORS_ORIGINS") or []
        
        if allowed_origins and not backend_cors_origins:
            origins = [i.strip().rstrip("/") for i in allowed_origins.split(",") if i.strip()]
            values["CORS_ORIGINS"] = origins
        return values

    # Google OAuth / Frontend
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    FRONTEND_URL: str = "http://localhost:3000"

    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 10
    FILE_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf"]

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = EduNexiaSettings()