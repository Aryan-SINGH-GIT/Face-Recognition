import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Support DATABASE_URL env var (for PostgreSQL on Render) or fall back to local SQLite
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Render gives postgres:// but SQLAlchemy 2.x needs postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    connect_args = {}
else:
    # Local development: SQLite
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DB_PATH = BASE_DIR / "access_control.db"
    DATABASE_URL = f"sqlite:///{DB_PATH}"
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI dependency for database session lifecycle."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
