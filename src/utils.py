from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat

from math import radians, cos, sin, asin, sqrt
import json
import logging


async def haversine(lat1, lon1, lat2, lon2):
    """
    Возвращает расстояние между двумя точками (в метрах) по координатам.
    """
    R = 6371000  # Радиус Земли в метрах
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


async def get_admin_ids():
    with open("admins.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return [admin["chat_id"] for admin in data["admins"]]


async def is_admin(telegram_id: int) -> bool:
    admin_ids = await get_admin_ids()
    return telegram_id in admin_ids


async def set_commands(bot: Bot):
    user_commands = [
        BotCommand(command="start", description="Перезапустить бота"),
        BotCommand(command="ping", description="Понг"),
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
            command="clear", description="Очистить отметки геолокации за сегодня"
        ),
        BotCommand(
            command="ping_all", description="Отправить сообщение всем пользователям"
        ),
        BotCommand(command="ping", description="Понг"),
        BotCommand(command="start_quest", description="Запустить опрос"),
        BotCommand(command="quest", description="Посмотреть результаты опроса"),
        BotCommand(command="clear_quest", description="Очистить результаты опроса"),
    ]
    try:
        admins = await get_admin_ids()
        for admin in admins:
            await bot.set_my_commands(
                admin_commands, scope=BotCommandScopeChat(chat_id=admin)
            )
    except Exception as e:
        logging.error(f"Ошибка установки админских команд: {e}")
