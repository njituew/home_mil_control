from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import json
from sqlalchemy import select
from db.utils import (
    get_all_users,
    delete_user_by_telegram_id,
    clear_today_control,
)
from db.models import User, TodayControl
from db.database import AsyncSessionLocal
import logging


router = Router()


def get_admin_ids():
    with open("admins.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return [admin["chat_id"] for admin in data["admins"]]


@router.message(Command("users"))
async def list_users(message: Message):
    admin_ids = get_admin_ids()
    if message.from_user.id not in admin_ids:
        await message.answer("У вас нет прав для этой команды.")
        logging.warning(f"Unauthorized access attempt by user {message.from_user.id}")
        return

    users = await get_all_users()
    if not users:
        await message.answer("Нет зарегистрированных пользователей.")
        return

    text = "Зарегистрированные пользователи:\n"
    for user in users:
        text += (
            f"Фамилия: {user.surname}, "
            f"Telegram ID: {user.telegram_id}, "
            f"Домашний адрес: {user.home_latitude}, {user.home_longitude}\n"
        )
    logging.info(f"Админ {message.from_user.id} запросил список пользователей.")
    await message.answer(text)


@router.message(Command("delete"))
async def delete_user(message: Message):
    admin_ids = get_admin_ids()
    if message.from_user.id not in admin_ids:
        await message.answer("У вас нет прав для этой команды.")
        logging.warning(f"Unauthorized access attempt by user {message.from_user.id}")
        return

    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Используйте команду в формате: /delete <telegram_id>")
        return

    telegram_id = int(args[1])
    await delete_user_by_telegram_id(telegram_id)
    logging.info(f"Админ {message.from_user.id} удалил пользователя с Telegram ID {telegram_id}.")
    await message.answer(f"Пользователь с Telegram ID {telegram_id} удалён (если был в базе).")


@router.message(Command("ping"))
async def ping(message: Message):
    await message.answer("понг")


@router.message(Command("clear"))
async def clear_control(message: Message):
    admin_ids = get_admin_ids()
    if message.from_user.id not in admin_ids:
        await message.answer("У вас нет прав для этой команды.")
        logging.warning(f"Unauthorized access attempt by user {message.from_user.id}")
        return

    await clear_today_control()
    logging.info(f"Админ {message.from_user.id} очистил таблицу TodayControl.")
    await message.answer("Таблица TodayControl успешно очищена.")


@router.message(Command("control"))
async def show_control_report(message: Message):
    admin_ids = get_admin_ids()
    if message.from_user.id not in admin_ids:
        await message.answer("У вас нет прав для этой команды.")
        logging.warning(f"Unauthorized access attempt by user {message.from_user.id}")
        return

    async with AsyncSessionLocal() as session:
        # Все пользователи
        users_result = await session.execute(select(User))
        users = users_result.scalars().all()

        # Все отметки за сегодня
        controls_result = await session.execute(select(TodayControl))
        controls = controls_result.scalars().all()
        controls_by_id = {c.telegram_id: c for c in controls}

        # Пользователи, прошедшие опрос и не дома
        not_home = [
            user.surname
            for user in users
            if user.telegram_id in controls_by_id and not controls_by_id[user.telegram_id].is_home
        ]

        # Пользователи, не прошедшие опрос
        not_checked = [
            user.surname
            for user in users
            if user.telegram_id not in controls_by_id
        ]

        # Формируем текст отчёта
        text = "Отчёт:\n"
        text += "\nНе дома:\n"
        text += "\n".join(not_home) if not_home else "Все дома или не отмечались"
        text += "\n\nНе прошли опрос:\n"
        text += "\n".join(not_checked) if not_checked else "Все отметились"

    logging.info(f"Админ {message.from_user.id} запросил отчёт по TodayControl.")
    
    await message.answer(text)


def register_admin_handlers(dp):
    dp.include_router(router)