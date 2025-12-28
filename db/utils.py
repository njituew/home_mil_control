from sqlalchemy import select, delete
from db.models import User, TodayControl, AlternativeLocation, Questionnaire
from db.database import AsyncSessionLocal
import logging


# Users
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


async def get_users_by_surname(surname: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.surname == surname))
        return result.scalars().all()


async def add_user(telegram_id: int, surname: str, latitude: float, longitude: float):
    async with AsyncSessionLocal() as session:
        user = User(
            telegram_id=telegram_id,
            surname=surname,
            home_latitude=latitude,
            home_longitude=longitude,
        )
        session.add(user)
        await session.commit()


async def get_all_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        return result.scalars().all()


async def delete_user_by_telegram_id(telegram_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if user:
            await session.delete(user)
            await session.commit()


# TodayControl
async def add_today_control(telegram_id: int, latitude: float, longitude: float):
    async with AsyncSessionLocal() as session:
        control = TodayControl(
            telegram_id=telegram_id,
            latitude=latitude,
            longitude=longitude,
        )
        session.add(control)
        await session.commit()


async def get_all_controls():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(TodayControl))
        return result.scalars().all()


async def get_today_control_by_id(telegram_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(TodayControl).where(TodayControl.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


async def clear_today_control():
    async with AsyncSessionLocal() as session:
        await session.execute(delete(TodayControl))
        await session.commit()
        logging.info("Таблица TodayControl очищена.")


# AlternativeLocation
async def add_alternative_location(
    telegram_id: int, latitude: float, longitude: float, comment: str = None
):
    """
    Добавляет альтернативную локацию пользователю.
    """
    async with AsyncSessionLocal() as session:
        location = AlternativeLocation(
            telegram_id=telegram_id,
            latitude=latitude,
            longitude=longitude,
            comment=comment,
        )
        session.add(location)
        await session.commit()


async def get_alternative_locations(telegram_id: int):
    """
    Получает все альтернативные локации конкретного пользователя.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AlternativeLocation).where(
                AlternativeLocation.telegram_id == telegram_id
            )
        )
        return result.scalars().all()


async def delete_alternative_location(location_id: int):
    """
    Удаляет альтернативную локацию по её ID.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(AlternativeLocation).where(AlternativeLocation.id == location_id)
        )
        location = result.scalar_one_or_none()
        if location:
            await session.delete(location)
            await session.commit()


async def get_all_alternative_locations():
    """
    Возвращает все альтернативные локации в базе.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(AlternativeLocation))
        return result.scalars().all()


# Questionnaire
async def add_user_questionnaire(
    telegram_id: int, surname: str, will_feed: bool = False
):
    async with AsyncSessionLocal() as session:
        user = Questionnaire(
            telegram_id=telegram_id,
            surname=surname,
            will_feed=will_feed,
        )
        session.add(user)
        await session.commit()


async def get_all_questionnaire():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Questionnaire))
        return result.scalars().all()


async def get_questionnaire_by_id(telegram_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Questionnaire).where(Questionnaire.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


async def clear_questionnaire():
    async with AsyncSessionLocal() as session:
        await session.execute(delete(Questionnaire))
        await session.commit()
        logging.info("All data cleared from Questionnaire table.")
