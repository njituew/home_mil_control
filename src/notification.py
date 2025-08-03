import json
from aiogram import Bot
from sqlalchemy import select
from db.models import User, TodayControl
from db.database import AsyncSessionLocal
from db.utils import clear_today_control
import logging


ADMINS_FILE = "admins.json"


async def send_reminder(bot: Bot):
    logging.info("Рассылка напоминаний пользователям")
    async with AsyncSessionLocal() as session:
        users_result = await session.execute(select(User))
        users = users_result.scalars().all()
        for user in users:
            try:
                await bot.send_message(
                    user.telegram_id,
                    "🚨 Отправьте геолокацию с 21:40 до 22:10."
                )
            except Exception as e:
                logging.error(f"Ошибка отправки пользователю {user.telegram_id}: {e}")


async def send_daily_report(bot: Bot):
    logging.info("Рассылка ежедневного отчёта администраторам")
    # Получаем список админов
    with open(ADMINS_FILE, "r", encoding="utf-8") as f:
        admins = [admin["chat_id"] for admin in json.load(f)["admins"]]

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

        text = "Ежедневный отчёт:\n"
        text += "\nНе дома:\n"
        text += "\n".join(not_home) if not_home else "Все дома или не отмечались"
        text += "\n\nНе прошли опрос:\n"
        text += "\n".join(not_checked) if not_checked else "Все отметились"

        # рассылка администраторам
        for admin_id in admins:
            try:
                await bot.send_message(admin_id, text)
            except Exception as e:
                print(f"Ошибка отправки админу {admin_id}: {e}")

        # очищаем таблицу TodayControl
        await clear_today_control()