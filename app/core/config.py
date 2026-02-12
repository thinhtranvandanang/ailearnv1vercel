from typing import List, Union, Optional, Any
from pydantic import AnyHttpUrl, validator, root_validator, BaseSettings

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
        if isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    # CORS
    # Đổi tên để Pydantic không tự động load từ env qua bộ parse JSON mặc định của nó
    BACKEND_CORS_ORIGINS: List[str] = []
    ALLOWED_ORIGINS: Optional[str] = None

    @validator("BACKEND_CORS_ORIGINS", pre=True, always=True)
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        # Ưu tiên đọc trực tiếp từ os.environ để tránh bộ parse JSON của Pydantic V1
        import os
        raw_val = os.environ.get("BACKEND_CORS_ORIGINS")
        
        if raw_val is None:
            # Nếu không có trong env, dùng giá trị được pass vào (nếu có)
            if isinstance(v, list): return v
            raw_val = v

        if not raw_val or raw_val == '""' or raw_val == "[]":
            return []
            
        if isinstance(raw_val, str):
            if raw_val.startswith("[") and raw_val.endswith("]"):
                try:
                    import json
                    return json.loads(raw_val)
                except:
                    pass
            return [i.strip().rstrip("/") for i in raw_val.split(",") if i.strip()]
        return raw_val if isinstance(raw_val, list) else []
    
    @root_validator
    def sync_cors_origins(cls, values):
        """Nếu có ALLOWED_ORIGINS trong .env, nạp vào BACKEND_CORS_ORIGINS."""
        allowed_origins = values.get("ALLOWED_ORIGINS")
        backend_cors_origins = values.get("BACKEND_CORS_ORIGINS")
        
        if allowed_origins and not backend_cors_origins:
            origins = [i.strip().rstrip("/") for i in allowed_origins.split(",") if i.strip()]
            values["BACKEND_CORS_ORIGINS"] = origins
        return values

    # Google OAuth / Frontend
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    FRONTEND_URL: str = "http://localhost:3000"

    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf"]

    @validator("ALLOWED_FILE_EXTENSIONS", pre=True, always=True)
    @classmethod
    def assemble_allowed_extensions(cls, v: Any) -> List[str]:
        import os
        raw_val = os.environ.get("ALLOWED_FILE_EXTENSIONS")
        if raw_val is None:
            if isinstance(v, list): return v
            raw_val = v
            
        if not raw_val:
            return ["jpg", "jpeg", "png", "pdf"]
            
        if isinstance(raw_val, str):
            if raw_val.startswith("["):
                try:
                    import json
                    return json.loads(raw_val)
                except:
                    pass
            return [i.strip() for i in raw_val.split(",") if i.strip()]
        return raw_val if isinstance(raw_val, list) else ["jpg", "jpeg", "png", "pdf"]

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()