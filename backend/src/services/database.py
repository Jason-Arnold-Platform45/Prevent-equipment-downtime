"""
Database connection management for Railway PostgreSQL.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from src.lib.config import get_settings
from src.lib.logging import get_logger

logger = get_logger(__name__)

# SQLAlchemy base for model definitions
Base = declarative_base()

# Global engine and session factory
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_database() -> None:
    """Initialize database connection pool."""
    global _engine, _session_factory

    settings = get_settings()

    logger.info("Initializing database connection", extra={
        "extra_fields": {"database": "railway"}
    })

    _engine = create_async_engine(
        settings.async_database_url,
        echo=settings.log_level == "DEBUG",
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )

    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # Test connection
    async with _engine.begin() as conn:
        await conn.execute(text("SELECT 1"))

    logger.info("Database connection established")


async def close_database() -> None:
    """Close database connection pool."""
    global _engine, _session_factory

    if _engine:
        logger.info("Closing database connection")
        await _engine.dispose()
        _engine = None
        _session_factory = None


def get_engine() -> AsyncEngine:
    """Get the database engine."""
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get the session factory."""
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database sessions."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database sessions."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def check_connection() -> bool:
    """Check if database connection is healthy."""
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
