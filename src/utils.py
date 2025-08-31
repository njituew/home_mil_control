from aiogram.types import Message
from math import radians, cos, sin, asin, sqrt
import json
import logging
from db.utils import (
    get_all_users,
    get_all_controls,
    get_all_questionnaire,
    get_user_by_telegram_id
)
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat


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
    user = await get_user_by_telegram_id(message.from_user.id)
    if user.telegram_id not in admin_ids:
        await message.answer("У вас нет прав для этой команды.")
        logging.warning(f"Пользователь {user.surname} ({user.telegram_id}) пытался использовать админскую команду.")
        return False
    return True


async def set_commands(bot: Bot):
    user_commands = [
        BotCommand(command="start", description="Перезапустить бота"),
        BotCommand(command="ping", description="Понг")
    ]
    try:
        await bot.set_my_commands(user_commands)
    except Exception as e:
        logging.error(f"Ошибка установки пользовательских команд: {e}")
    
    admin_commands = [
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
    try:
        admins = await get_admin_ids()
        for admin in admins:
            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin))
    except Exception as e:
        logging.error(f"Ошибка установки админских команд: {e}")


async def generate_report() -> str:
    users = await get_all_users()
    controls = await get_all_controls()
    controls_by_id = {c.telegram_id: c.distance for c in controls}

    at_home, not_at_home, not_checked = [], [], []
    for user in users:
        if user.telegram_id in controls_by_id:
            # check if user is at home
            if controls_by_id[user.telegram_id] <= 250:
                at_home.append(
                    f"{user.surname} ✅"
                )
            else:
                not_at_home.append(
                    f"{user.surname} ({controls_by_id[user.telegram_id]/1000:.2f} км от дома)"
                )
        else: 
            not_checked.append(user.surname)

    text = "Отчёт:\n"
    text += "\nНе дома:\n"
    text += "\n".join(not_at_home) if not_at_home else "Все дома или все не отметились"
    text += "\n\nНе прошли опрос:\n"
    text += "\n".join(not_checked) if not_checked else "Все отметились"
    text += "\n\nДома:\n"
    text += "\n".join(at_home) if at_home else "Все не дома или все не отметились"
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