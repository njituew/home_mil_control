import os
import re

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import get_database_dsn


def _ensure_db_dir(dsn: str) -> None:
    """Create the database directory if it does not exist."""
    match = re.search(r"sqlite(?:\+\w+)?:///(.+)", dsn)
    if match:
        db_path = match.group(1)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)


_dsn = get_database_dsn()
_ensure_db_dir(_dsn)
engine = create_async_engine(_dsn)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def init_db():
    from db import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
