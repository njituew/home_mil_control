from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.utils import get_all_users, get_all_controls
from src.utils import get_admin_ids
from src.reports import generate_report
import logging


async def send_reminder(bot: Bot):
    logging.info("Рассылка напоминаний пользователям")
    users = await get_all_users()
    for user in users:
        try:
            await bot.send_message(
                user.telegram_id, "🚨 Отправьте свою геолокацию до 22:10."
            )
        except Exception as e:
            logging.error(f"Ошибка отправки пользователю {user.telegram_id}: {e}")


async def send_last_chance(bot: Bot):
    logging.info("Отправка последнего предупреждения пользователям")

    users = await get_all_users()
    controls = await get_all_controls()

    not_checked = [
        user
        for user in users
        if user.telegram_id not in {c.telegram_id for c in controls}
    ]

    for user in not_checked:
        try:
            await bot.send_message(
                user.telegram_id, "🚨 Осталось 5 минут чтобы отправить свою локацию."
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
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            (InlineKeyboardButton(text="✅", callback_data="questionnaire_answer_1"),),
            (InlineKeyboardButton(text="❌", callback_data="questionnaire_answer_2"),),
        ]
    )
    text = f"text\n"
    users = await get_all_users()
    for user in users:
        try:
            await bot.send_message(user.telegram_id, text, reply_markup=keyboard)
        except Exception as e:
            logging.error(f"Ошибка отправки пользователю {user.telegram_id}: {e}")
