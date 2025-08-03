from aiogram.types import Message
from dotenv import load_dotenv
import os
from math import radians, cos, sin, asin, sqrt
import json
import logging


def haversine(lat1, lon1, lat2, lon2):
    """
    Возвращает расстояние между двумя точками (в метрах) по координатам.
    """
    R = 6371000  # Радиус Земли в метрах
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

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

def get_admin_ids():
    with open("admins.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return [admin["chat_id"] for admin in data["admins"]]

async def is_admin(message: Message):
    admin_ids = get_admin_ids()
    user_id = message.from_user.id
    if user_id not in admin_ids:
        await message.answer("У вас нет прав для этой команды.")
        logging.warning(f"Unauthorized access attempt by user {user_id}")
        return False
    return True