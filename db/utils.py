from sqlalchemy import select, delete
from db.models import User, TodayControl, NotHomeDistance, Questionnaire
from db.database import AsyncSessionLocal
import logging


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


async def add_not_home_distance(telegram_id: int, distance: float):
    async with AsyncSessionLocal() as session:
        distance_record = NotHomeDistance(telegram_id=telegram_id, distance=distance)
        session.add(distance_record)
        await session.commit()


async def delete_user_by_telegram_id(telegram_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if user:
            await session.delete(user)
            await session.commit()


async def clear_today_control():
    async with AsyncSessionLocal() as session:
        await session.execute(delete(TodayControl))
        await session.commit()


async def clear_not_home_distance():
    async with AsyncSessionLocal() as session:
        await session.execute(delete(NotHomeDistance))
        await session.commit()


async def clear_data():
    async with AsyncSessionLocal() as session:
        await session.execute(delete(TodayControl))
        await session.execute(delete(NotHomeDistance))
        await session.commit()
        logging.info("All data cleared from TodayControl and NotHomeDistance tables.")


# опросы
async def add_user_questionnaire(telegram_id: int, surname: str, will_feed: bool = False):
    async with AsyncSessionLocal() as session:
        user = Questionnaire(
            telegram_id=telegram_id,
            surname=surname,
            will_feed=will_feed,
        )
        session.add(user)
        await session.commit()


async def clear_questionnaire():
    async with AsyncSessionLocal() as session:
        await session.execute(delete(Questionnaire))
        await session.commit()
        logging.info("All data cleared from Questionnaire table.")