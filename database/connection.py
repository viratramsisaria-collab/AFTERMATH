
"""SQLite connection and session management for AFTERMATH."""

import os
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import get_settings


Base = declarative_base()


def _database_url() -> str:
    """Resolve the database URL from environment or application settings."""

    configured_path = os.getenv("DATABASE_PATH")

    if not configured_path:
        configured_path = str(get_settings().database_path)

    if configured_path == ":memory:":
        return "sqlite://"

    path = Path(configured_path).expanduser()

    if not path.is_absolute():
        path = Path.cwd() / path

    path.parent.mkdir(parents=True, exist_ok=True)

    return f"sqlite:///{path.as_posix()}"


@lru_cache(maxsize=1)
def get_engine():
    """Create and cache the SQLite engine."""

    engine = create_engine(
        _database_url(),
        connect_args={"check_same_thread": False},
        future=True,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


@lru_cache(maxsize=1)
def get_session_factory():
    """Return the cached SQLAlchemy session factory."""

    return sessionmaker(
        bind=get_engine(),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )


@contextmanager
def session_scope():
    """Provide a transactional database session."""

    session = get_session_factory()()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Create all registered database tables."""

    # Import models so their tables are registered on Base.metadata.
    from database import models  # noqa: F401

    Base.metadata.create_all(bind=get_engine())


def close_database() -> None:
    """Dispose of the engine and clear cached connections."""

    engine = get_engine()
    engine.dispose()

    get_session_factory.cache_clear()
    get_engine.cache_clear()
