from typing import List, Union, Optional
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
    BACKEND_CORS_ORIGINS: List[str] = []
    ALLOWED_ORIGINS: Optional[str] = None

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        # Handle None or empty string
        if v is None or v == "" or v == "[]":
            return []
        if isinstance(v, str) and not v.startswith("["):
            # Tách chuỗi bằng dấu phẩy và loại bỏ khoảng trắng + dấu / ở cuối
            return [i.strip().rstrip("/") for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return [str(i).strip().rstrip("/") for i in v]
        return []
    
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

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()