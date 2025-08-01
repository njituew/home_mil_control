import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.register import register_handlers
from db.database import init_db
from src.utils import get_bot_token


async def main():
    bot_token = get_bot_token()
    bot = Bot(bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    
    await init_db()
    
    register_handlers(dp)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())