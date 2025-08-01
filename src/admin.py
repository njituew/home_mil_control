from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from db.models import User
from db.database import AsyncSessionLocal
from sqlalchemy import select
import json

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

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
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

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            await message.answer("Пользователь с таким Telegram ID не найден.")
            return

        await session.delete(user)
        await session.commit()
        await message.answer(f"Пользователь с Telegram ID {telegram_id} удалён.")

def register_admin_handlers(dp):
    dp.include_router(router)