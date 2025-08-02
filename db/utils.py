from sqlalchemy import select, delete
from db.models import User, TodayControl
from db.database import AsyncSessionLocal

async def is_user_registered(telegram_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none() is not None

async def get_user_by_telegram_id(telegram_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

async def add_user(telegram_id: int, surname: str, latitude: float, longitude: float):
    async with AsyncSessionLocal() as session:
        user = User(
            telegram_id=telegram_id,
            surname=surname,
            home_latitude=latitude,
            home_longitude=longitude
        )
        session.add(user)
        await session.commit()

async def get_all_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        return result.scalars().all()

async def get_today_control_by_telegram_id(telegram_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(TodayControl).where(TodayControl.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

async def add_today_control(telegram_id: int, is_home: bool):
    async with AsyncSessionLocal() as session:
        control = TodayControl(telegram_id=telegram_id, is_home=is_home)
        session.add(control)
        await session.commit()

async def clear_today_control():
    async with AsyncSessionLocal() as session:
        await session.execute(delete(TodayControl))
        await session.commit()

async def delete_user_by_telegram_id(telegram_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if user:
            await session.delete(user)
            await session.commit()