"""
Database configuration and session management

For demo purposes, we use SQLite which requires:
- No separate database server
- No configuration needed
- Database stored as a file (openride_demo.db)
- Perfect for hackathon demos and testing
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .settings import get_settings

settings = get_settings()

# Create SQLAlchemy engine with SQLite-specific configuration
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for demo - no threading checks needed for async FastAPI
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},  # Required for SQLite with FastAPI
        echo=False  # Set to True for SQL debugging
    )
else:
    # PostgreSQL configuration (for production)
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    
    For SQLite demo:
    - Creates openride_demo.db file if it doesn't exist
    - Creates all tables automatically
    - No manual database setup required
    """
    Base.metadata.create_all(bind=engine)
    
    # Print database status for demo
    if settings.DATABASE_URL.startswith("sqlite"):
        db_file = settings.DATABASE_URL.replace("sqlite:///", "")
        print(f"✅ SQLite database initialized: {db_file}")
        print(f"✅ Demo database ready - no setup required!")
