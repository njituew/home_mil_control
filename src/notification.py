from aiogram import Bot
from sqlalchemy import select
from db.models import TodayControl
from db.database import AsyncSessionLocal
from db.utils import clear_today_control, get_all_users
from src.utils import generate_report, get_admin_ids
import logging


ADMINS_FILE = "admins.json"


async def send_reminder(bot: Bot):
    logging.info("Рассылка напоминаний пользователям")
    async with AsyncSessionLocal() as session:
        users = await get_all_users()
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
    
    admins = await get_admin_ids()
    report = await generate_report()

    # рассылка
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, report)
        except Exception as e:
            print(f"Ошибка отправки админу {admin_id}: {e}")

    # очищаем таблицу TodayControl
    await clear_today_control()


async def send_last_chance(bot: Bot):
    logging.info("Отправка последнего предупреждения пользователям")
    async with AsyncSessionLocal() as session:
        users = await get_all_users()
        
        controls_result = await session.execute(select(TodayControl))
        controls = controls_result.scalars().all()
        controls_by_id = {c.telegram_id: c for c in controls}
        
        not_checked = [
            user
            for user in users
            if user.telegram_id not in controls_by_id
        ]
        
        for user in not_checked:
            try:
                await bot.send_message(
                    user.telegram_id,
                    "🚨 Осталось 5 минут чтобы отправить свою локацию."
                )
            except Exception as e:
                logging.error(f"Ошибка отправки пользователю {user.telegram_id}: {e}")