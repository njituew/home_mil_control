from aiogram.types import Message
from math import radians, cos, sin, asin, sqrt
import json
import logging
from db.utils import (
    get_all_users,
    get_all_controls,
    get_all_distances,
    get_all_questionnaire
)


async def haversine(lat1, lon1, lat2, lon2):
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


async def get_admin_ids():
    with open("admins.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return [admin["chat_id"] for admin in data["admins"]]


async def is_admin(message: Message):
    admin_ids = await get_admin_ids()
    user_id = message.from_user.id
    if user_id not in admin_ids:
        await message.answer("У вас нет прав для этой команды.")
        logging.warning(f"Unauthorized access attempt by user {user_id}")
        return False
    return True


async def generate_report() -> str:
    users = await get_all_users()
    
    controls = await get_all_controls()
    controls_by_id = {c.telegram_id: c for c in controls}
    
    distances = await get_all_distances()
    distances_by_id = {d.telegram_id: d.distance for d in distances}

    not_home = [
        f"{user.surname} ({distances_by_id[user.telegram_id]/1000:.2f} км от дома)"
        for user in users
        if user.telegram_id in controls_by_id and not controls_by_id[user.telegram_id].is_home
    ]

    not_checked = [
        user.surname
        for user in users
        if user.telegram_id not in controls_by_id
    ]

    text = "Отчёт:\n"
    text += "\nНе дома:\n"
    text += "\n".join(not_home) if not_home else "Все дома или не отмечались"
    text += "\n\nНе прошли опрос:\n"
    text += "\n".join(not_checked) if not_checked else "Все отметились"
    return text


async def generate_report_quest() -> str:
    users = await get_all_users()

    questionnaires = await get_all_questionnaire()
    questionnaires_by_id = {q.telegram_id: q for q in questionnaires}

    will_feed_users = [
        f"{user.surname} {'✅' if questionnaires_by_id[user.telegram_id].will_feed else '❌'}"
        for user in users
        if user.telegram_id in questionnaires_by_id
    ]
    
    not_answered = [
        user.surname
        for user in users
        if user.telegram_id not in questionnaires_by_id
    ]

    text = "Отчёт по опросу:\n"
    text += "\nРезультаты опроса:\n"
    text += "\n".join(will_feed_users) if will_feed_users else "Никто не прошёл опрос"
    text += "\n\nНе прошли опрос:\n"
    text += "\n".join(not_answered) if not_answered else "Все отметились"
    return text