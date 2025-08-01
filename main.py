import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.handlers import register_handlers
from db.database import init_db
from src.utils import get_bot_token
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from src.notification import send_daily_report


async def main():
    bot_token = get_bot_token()
    bot = Bot(bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    
    await init_db()
    register_handlers(dp)
    # Настройка планировщика
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(send_daily_report, CronTrigger(hour=0, minute=6))
    scheduler.start()
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())