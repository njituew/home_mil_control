from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from db.utils import (
    get_all_users,
    get_user_by_telegram_id,
    delete_user_by_telegram_id,
    clear_today_control,
    clear_questionnaire,
)
from src.notification import send_questionnaire
from src.utils import is_admin, generate_report, generate_report_quest
import logging
from functools import wraps


router = Router()


def admin_only(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        user = await get_user_by_telegram_id(message.from_user.id)
        if not await is_admin(message.from_user.id):
            await message.answer("У вас нет прав для этой команды.")
            logging.warning(
                f"Пользователь {user.surname} "
                f"({message.from_user.id}) пытался использовать админскую команду."
            )
            return
        return await func(message, *args, **kwargs)

    return wrapper


@router.message(Command("users"))
@admin_only
async def list_users(message: Message):
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
    user = await get_user_by_telegram_id(message.from_user.id)
    logging.info(
        f"Админ {user.surname} ({user.telegram_id}) запросил список пользователей."
    )
    await message.answer(text)


@router.message(Command("delete"))
@admin_only
async def delete_user(message: Message):
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Используйте команду в формате: /delete <telegram_id>")
        return

    telegram_id = int(args[1])
    await delete_user_by_telegram_id(telegram_id)
    user = await get_user_by_telegram_id(message.from_user.id)
    # TODO: AttributeError: 'NoneType' object has no attribute 'surname'
    logging.info(
        f"Админ {user.surname} ({user.telegram_id}) удалил пользователя с Telegram ID {telegram_id}."
    )
    await message.answer(
        f"Пользователь с Telegram ID {telegram_id} удалён (если был в базе)."
    )


@router.message(Command("clear"))
@admin_only
async def clear_control(message: Message):
    await clear_today_control()
    user = await get_user_by_telegram_id(message.from_user.id)
    logging.info(
        f"Админ {user.surname} ({user.telegram_id}) очистил таблицу TodayControl."
    )
    await message.answer("Сегодняшние отметки успешно удалены.")


@router.message(Command("control"))
@admin_only
async def show_control_report(message: Message):
    report = await generate_report()
    user = await get_user_by_telegram_id(message.from_user.id)
    logging.info(
        f"Админ {user.surname} ({user.telegram_id}) запросил отчёт по TodayControl."
    )
    await message.answer(report)


@router.message(Command("ping_all"))
@admin_only
async def ping_all(message: Message):
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
            logging.error(
                f"Ошибка отправки сообщения пользователю {user.telegram_id}: {e}"
            )

    user = await get_user_by_telegram_id(message.from_user.id)
    logging.info(
        f"Админ {user.surname} ({user.telegram_id}) отправил массовое сообщение '{text}' {count} пользователям."
    )
    await message.answer(f"Сообщение отправлено {count} пользователям.")


@router.message(Command("start_quest"))
@admin_only
async def start_questionnaire(message: Message):
    await send_questionnaire(message.bot)
    user = await get_user_by_telegram_id(message.from_user.id)
    logging.info(
        f"Админ {user.surname} ({user.telegram_id}) запустил опрос по питанию."
    )


@router.message(Command("quest"))
@admin_only
async def questionnaire(message: Message):
    report = await generate_report_quest()
    user = await get_user_by_telegram_id(message.from_user.id)
    logging.info(f"Админ {user.surname} ({user.telegram_id}) запросил отчёт по опросу.")
    await message.answer(report)


@router.message(Command("clear_quest"))
@admin_only
async def clear_quest(message: Message):
    await clear_questionnaire()
    user = await get_user_by_telegram_id(message.from_user.id)
    logging.info(
        f"Админ {user.surname} ({user.telegram_id}) очистил таблицу Questionnaire."
    )
    await message.answer("Таблица Questionnaire успешно очищена.")


def register_admin_handlers(dp):
    dp.include_router(router)
