import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from routers.registration import register_registration_handlers
from routers.user import register_user_handlers
from routers.admin import register_admin_handlers

from db.database import init_db
from src.config import get_bot_token, init_logging
from src.scheduler import init_scheduler
from src.utils import set_commands


async def main():
    bot = Bot(get_bot_token())
    logging = init_logging()
    await init_db()

    dp = Dispatcher(storage=MemoryStorage())
    register_registration_handlers(dp)
    register_admin_handlers(dp)
    register_user_handlers(dp)

    scheduler = init_scheduler(bot)
    scheduler.start()

    await set_commands(bot)

    try:
        logging.info("Бот запускается...")
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        logging.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
