from dotenv import load_dotenv
import os
from aiogram import Bot
from aiogram.types import BotCommand


def get_bot_token():
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN is not set in the environment variables.")
    return bot_token


def get_database_dsn():
    load_dotenv()
    database_dsn = os.getenv("DATABASE_DSN")
    if not database_dsn:
        raise ValueError("DATABASE_DSN is not set in the environment variables.")
    return database_dsn


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="users", description="Список пользователей"),
        BotCommand(command="delete", description="Удалить пользователя по Telegram ID"),
        BotCommand(command="control", description="Посмотреть текущие отметки геолокации"),
        BotCommand(command="clear", description="Очистить отметки геолокации за сегодня"),
        BotCommand(command="ping_all", description="Отправить сообщение всем пользователям"),
        BotCommand(command="ping", description="Понг"),
        BotCommand(command="start_quest", description="Запустить опрос"),
        BotCommand(command="quest", description="Посмотреть результаты опроса"),
        BotCommand(command="clear_quest", description="Очистить результаты опроса")
    ]
    await bot.set_my_commands(commands)