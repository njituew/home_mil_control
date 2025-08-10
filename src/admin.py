from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from db.utils import (
    get_all_users,
    delete_user_by_telegram_id,
    clear_data,
    clear_questionnaire
)
from src.notification import send_questionnaire
from src.utils import is_admin, generate_report, generate_report_quest
from src.config import set_commands
import logging


router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message):
    if not await is_admin(message):
        return
    await set_commands(message.bot)


@router.message(Command("users"))
async def list_users(message: Message):
    if not await is_admin(message):
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
    logging.info(f"Админ {message.from_user.id} запросил список пользователей.")
    await message.answer(text)


@router.message(Command("delete"))
async def delete_user(message: Message):
    if not await is_admin(message):
        return

    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Используйте команду в формате: /delete <telegram_id>")
        return

    telegram_id = int(args[1])
    await delete_user_by_telegram_id(telegram_id)
    logging.info(f"Админ {message.from_user.id} удалил пользователя с Telegram ID {telegram_id}.")
    await message.answer(f"Пользователь с Telegram ID {telegram_id} удалён (если был в базе).")


@router.message(Command("clear"))
async def clear_control(message: Message):
    if not await is_admin(message):
        return
    await clear_data()
    logging.info(f"Админ {message.from_user.id} очистил таблицу TodayControl и NotHomeDistance.")
    await message.answer("Сегодняшние отметки успешно удалены.")


@router.message(Command("control"))
async def show_control_report(message: Message):
    if not await is_admin(message):
        return
    report = await generate_report()
    logging.info(f"Админ {message.from_user.id} запросил отчёт по TodayControl.")
    await message.answer(report)


@router.message(Command("ping_all"))
async def ping_all(message: Message):
    if not await is_admin(message):
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].strip():
        await message.answer("Используйте команду в формате: /ping_all {текст}")
        return

    text = args[1].strip()
    users = await get_all_users()
    count = 0
    for user in users:
        try:
            await message.bot.send_message(user.telegram_id, text)
            count += 1
        except Exception as e:
            logging.error(f"Ошибка отправки сообщения пользователю {user.telegram_id}: {e}")

    logging.info(f"Админ {message.from_user.id} отправил массовое сообщение '{text}' {count} пользователям.")
    await message.answer(f"Сообщение отправлено {count} пользователям.")


@router.message(Command("start_quest"))
async def start_questionnaire(message: Message):
    if not await is_admin(message):
        return
    await send_questionnaire(message.bot)
    logging.info(f"Админ {message.from_user.id} запустил опрос по питанию.")


@router.message(Command("quest"))
async def questionnaire(message: Message):
    if not await is_admin(message):
        return
    report = await generate_report_quest()
    logging.info(f"Админ {message.from_user.id} запросил отчёт по опросу.")
    await message.answer(report)


@router.message(Command("clear_quest"))
async def clear_quest(message: Message):
    if not await is_admin(message):
        return
    await clear_questionnaire()
    logging.info(f"Админ {message.from_user.id} очистил таблицу Questionnaire.")
    await message.answer("Таблица Questionnaire успешно очищена.")


def register_admin_handlers(dp):
    dp.include_router(router)