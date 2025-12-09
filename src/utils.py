from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat
import json
import logging


async def get_admin_ids():
    with open("admins.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return [admin["chat_id"] for admin in data["admins"]]


async def is_admin(telegram_id: int) -> bool:
    admin_ids = await get_admin_ids()
    return telegram_id in admin_ids


async def set_commands(bot: Bot):
    user_commands = [
        BotCommand(command="ping", description="Понг"),
        BotCommand(command="info", description="Откуда ноги растут"),
    ]
    try:
        await bot.set_my_commands(user_commands)
    except Exception as e:
        logging.error(f"Ошибка установки пользовательских команд: {e}")

    admin_commands = [
        BotCommand(command="users", description="Список пользователей"),
        BotCommand(command="delete", description="Удалить пользователя по Telegram ID"),
        BotCommand(
            command="control", description="Посмотреть текущие отметки геолокации"
        ),
        BotCommand(
            command="add_alt",
            description="Добавление альтернативной локации для пользователя. <telegram_id> <latitude> <longitude> [комментарий]",
        ),
        BotCommand(
            command="user_alt",
            description="Показать все альтернативные локации пользователя. /alt_list <telegram_id>",
        ),
        BotCommand(
            command="all_alt",
            description="Показать все альтернативные локации.",
        ),
        BotCommand(
            command="del_alt", description="Удалить альтернативную локацию по ID."
        ),
        BotCommand(
            command="ping_all", description="Отправить сообщение всем пользователям"
        ),
        BotCommand(command="ping", description="Понг"),
        BotCommand(command="start_quest", description="Запустить опрос"),
        BotCommand(command="quest", description="Посмотреть результаты опроса"),
        BotCommand(command="clear_quest", description="Очистить результаты опроса"),
        BotCommand(
            command="clear", description="Очистить отметки геолокации за сегодня"
        ),
        BotCommand(command="info", description="Откуда ноги растут"),
    ]
    try:
        admins = await get_admin_ids()
        for admin in admins:
            await bot.set_my_commands(
                admin_commands, scope=BotCommandScopeChat(chat_id=admin)
            )
    except Exception as e:
        logging.error(f"Ошибка установки админских команд: {e}")
