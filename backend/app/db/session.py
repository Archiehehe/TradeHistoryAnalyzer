from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings


@lru_cache(maxsize=1)
def get_engine():
    settings = get_settings()
    if not settings.database_dsn:
        raise RuntimeError("DATABASE_URL or NEON_DATABASE_URL must be configured before creating the engine.")
    return create_engine(settings.database_dsn, future=True, pool_pre_ping=True)


def warm_up_engine(settings: Settings) -> None:
    if settings.database_dsn:
        get_engine()


def get_session_factory():
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)


def get_db_session() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()

