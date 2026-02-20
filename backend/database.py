"""
SQLAlchemy database connection and session management.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import config

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    config.DATABASE_URI,
    pool_size=config.POOL_SIZE,
    max_overflow=config.MAX_OVERFLOW,
    pool_timeout=config.POOL_TIMEOUT,
    pool_pre_ping=True,  # Verify connections before use
    echo=False
)

# Session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base class for ORM models
Base = declarative_base()


def get_session():
    """Create a new database session. Use as context manager."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_db_session():
    """Create and return a new database session (non-generator version)."""
    return SessionLocal()


def test_connection():
    """Test database connectivity."""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
