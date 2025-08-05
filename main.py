import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.handlers import register_handlers
from src.admin import register_admin_handlers
from db.database import init_db
from src.config import get_bot_token
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from src.notification import (
    send_reminder,
    send_daily_report,
    send_last_chance,
)
import pytz
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log", encoding="utf-8", mode="a")
    ]
)


async def main():
    logging.info("Бот запускается...")
    bot_token = get_bot_token()
    bot = Bot(bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    
    await init_db()
    register_handlers(dp)
    register_admin_handlers(dp)

    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Europe/Moscow"))
    scheduler.add_job(
        send_reminder,
        CronTrigger(hour=18, minute=40),
        args=[bot],
        id="send_reminder",
        replace_existing=True
    )
    scheduler.add_job(
        send_last_chance,
        CronTrigger(hour=19, minute=5),
        args=[bot],
        id="send_last_chance",
        replace_existing=True
    )
    scheduler.add_job(
        send_daily_report,
        CronTrigger(hour=19, minute=12),
        args=[bot],
        id="send_daily_report",
        replace_existing=True
    )
    scheduler.start()
    
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        logging.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())