from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.utils import get_database_dsn

# Настройка асинхронной базы данных SQLite
database_dsn = get_database_dsn()
engine = create_async_engine(database_dsn)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()

async def init_db():
    from db.models import User  # Импорт модели для создания таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)