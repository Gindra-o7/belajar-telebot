import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database URL dari environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/telebot")

# Create engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class untuk models
Base = declarative_base()

def get_db():
    """Dependency untuk mendapatkan database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database - buat semua tabel"""
    from app.database import models  # Import models setelah Base dibuat
    Base.metadata.create_all(bind=engine)