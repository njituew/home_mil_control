import asyncio
from src.bot import create_bot


async def main():
    bot, dp, scheduler, logging = await create_bot()

    try:
        logging.info("Бот запускается...")
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        logging.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
