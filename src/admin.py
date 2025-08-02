from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import json
from db.utils import (
    get_all_users,
    delete_user_by_telegram_id,
    clear_today_control,
)


router = Router()


def get_admin_ids():
    with open("admins.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return [admin["chat_id"] for admin in data["admins"]]


@router.message(Command("users"))
async def list_users(message: Message):
    admin_ids = get_admin_ids()
    if message.from_user.id not in admin_ids:
        await message.answer("У вас нет прав для этой команды.")
        return

    users = await get_all_users()
    if not users:
        await message.answer("Нет зарегистрированных пользователей.")
        return

    text = "Зарегистрированные пользователи:\n"
    for user in users:
        text += (
            f"Фамилия: {user.surname}, "
            f"Telegram ID: {user.telegram_id}, "
            f"Домашний адрес: {user.home_latitude}, {user.home_longitude}\n"
        )
    await message.answer(text)


@router.message(Command("delete"))
async def delete_user(message: Message):
    admin_ids = get_admin_ids()
    if message.from_user.id not in admin_ids:
        await message.answer("У вас нет прав для этой команды.")
        return

    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Используйте команду в формате: /delete <telegram_id>")
        return

    telegram_id = int(args[1])
    await delete_user_by_telegram_id(telegram_id)
    await message.answer(f"Пользователь с Telegram ID {telegram_id} удалён (если был в базе).")


@router.message(Command("clear"))
async def clear_control(message: Message):
    admin_ids = get_admin_ids()
    if message.from_user.id not in admin_ids:
        await message.answer("У вас нет прав для этой команды.")
        return

    await clear_today_control()
    await message.answer("Таблица TodayControl успешно очищена.")


def register_admin_handlers(dp):
    dp.include_router(router)