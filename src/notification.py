from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from db.models import TodayControl
from db.database import AsyncSessionLocal
from db.utils import get_all_users
from src.utils import generate_report, get_admin_ids
import logging


ADMINS_FILE = "admins.json"


async def send_reminder(bot: Bot):
    logging.info("Рассылка напоминаний пользователям")
    users = await get_all_users()
    for user in users:
        try:
            await bot.send_message(
                user.telegram_id,
                "🚨 Отправьте геолокацию с 21:40 до 22:10."
            )
        except Exception as e:
            logging.error(f"Ошибка отправки пользователю {user.telegram_id}: {e}")


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


async def send_daily_report(bot: Bot):
    logging.info("Рассылка ежедневного отчёта администраторам")
    
    admins = await get_admin_ids()
    report = await generate_report()

    for admin_id in admins:
        try:
            await bot.send_message(admin_id, report)
        except Exception as e:
            print(f"Ошибка отправки админу {admin_id}: {e}")


async def send_questionnaire(bot: Bot):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        (InlineKeyboardButton(text="✅ Я буду питаться", callback_data="questionnaire_feeding_yes"),),
        (InlineKeyboardButton(text="❌ Я не буду питаться", callback_data="questionnaire_feeding_no"),)
    ])
    text = (
        f"Товарищи, напоминаю про новые правила котлового довольствия:\n"
        f"Если на вас пишется рапорт, то вы записываетесь на все обеды по будним дням, "
        f"и даже если не будете питаться в конктретный день - всё равно за него заплатите.\n"
        f"В очередной раз провожу опрос, кто будет питаться в столовой ППД. "
        f"Если вы согласны питаться в столовой ППД на таких условиях, проголосуйте ниже соответствующей кнопкой.\n"
        f"В понедельник будет писаться рапорт, кто не успел будет писать его за себя самостоятельно."
    )
    users = await get_all_users()
    for user in users:
        try:
            await bot.send_message(
                user.telegram_id,
                text,
                reply_markup=keyboard
            )
        except Exception as e:
            logging.error(f"Ошибка отправки пользователю {user.telegram_id}: {e}")