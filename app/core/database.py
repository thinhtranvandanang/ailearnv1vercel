from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Import all models so that SQLAlchemy can resolve relationship() 
# string references like "Session" when mappers are configured.
# This import is required for proper mapper configuration at application startup.
from app.db import base  # noqa: F401

# Engine setup
db_url = settings.DATABASE_URL
print(f"DEBUG: Initial DATABASE_URL scheme: {db_url.split('://')[0] if '://' in db_url else 'None'}")

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
elif db_url.startswith("postgresql://") and "+psycopg" not in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

print(f"DEBUG: Final DATABASE_URL scheme: {db_url.split('://')[0] if '://' in db_url else 'None'}")
engine = create_engine(db_url, pool_pre_ping=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)