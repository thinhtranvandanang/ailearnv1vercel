from typing import List, Union, Optional, Any
from pydantic import AnyHttpUrl, validator, root_validator, BaseSettings, Field

class Settings(BaseSettings):
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
    # Đổi tên hoàn toàn để Pydantic V1 không bao giờ nhầm lẫn với biến môi trường trùng tên
    BACKEND_CORS_ORIGINS_FIX: List[str] = []
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
                    values["BACKEND_CORS_ORIGINS_FIX"] = json.loads(raw_cors)
                except:
                    values["BACKEND_CORS_ORIGINS_FIX"] = [i.strip() for i in raw_cors.split(",") if i.strip()]
            else:
                 values["BACKEND_CORS_ORIGINS_FIX"] = [i.strip() for i in raw_cors.split(",") if i.strip()]
        
        # Manual load ALLOWED_FILE_EXTENSIONS
        raw_ext = os.environ.get("ALLOWED_FILE_EXTENSIONS")
        if raw_ext:
            if raw_ext.startswith("["):
                try:
                    values["ALLOWED_FILE_EXTENSIONS"] = json.loads(raw_ext)
                except:
                    values["ALLOWED_FILE_EXTENSIONS"] = [i.strip() for i in raw_ext.split(",") if i.strip()]
            else:
                values["ALLOWED_FILE_EXTENSIONS"] = [i.strip() for i in raw_ext.split(",") if i.strip()]

        return values
    
    @root_validator
    def sync_cors_origins_logic(cls, values):
        """Nếu có ALLOWED_ORIGINS trong .env, nạp vào BACKEND_CORS_ORIGINS_FIX."""
        allowed_origins = values.get("ALLOWED_ORIGINS")
        backend_cors_origins = values.get("BACKEND_CORS_ORIGINS_FIX") or []
        
        if allowed_origins and not backend_cors_origins:
            origins = [i.strip().rstrip("/") for i in allowed_origins.split(",") if i.strip()]
            values["BACKEND_CORS_ORIGINS_FIX"] = origins
        return values

    # Google OAuth / Frontend
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    FRONTEND_URL: str = "http://localhost:3000"

    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_EXTENSIONS: List[str] = Field(["jpg", "jpeg", "png", "pdf"], env="DUMMY_VAR_EXT")

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()