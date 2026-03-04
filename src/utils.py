from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat
import logging

from db.utils import get_admin_ids


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
        BotCommand(command="user", description="Информация о пользователе по фамилии или Telegram ID"),
        BotCommand(command="delete", description="Удалить пользователя по Telegram ID"),
        BotCommand(command="control", description="Посмотреть текущие отметки геолокации"),
        BotCommand(command="clear", description="Очистить отметки геолокации за сегодня"),
        BotCommand(command="where_is", description="Посмотреть последнюю локацию пользователя по Telegram ID"),
        BotCommand(command="add_alt", description="Добавить альтернативную локацию: <telegram_id> <latitude> <longitude> [комментарий]"),
        BotCommand(command="user_alt", description="Альтернативные локации пользователя по Telegram ID"),
        BotCommand(command="all_alt", description="Все альтернативные локации"),
        BotCommand(command="del_alt", description="Удалить альтернативную локацию по ID"),
        BotCommand(command="ping_all", description="Отправить сообщение всем пользователям"),
        BotCommand(command="admins", description="Список администраторов"),
        BotCommand(command="add_admin", description="Добавить администратора по Telegram ID"),
        BotCommand(command="delete_admin", description="Удалить администратора по Telegram ID"),
        BotCommand(command="ping", description="Понг"),
        BotCommand(command="info", description="Откуда ноги растут"),
        # Deleted feature
        # BotCommand(command="start_quest", description="Запустить опрос"),
        # BotCommand(command="quest", description="Посмотреть результаты опроса"),
        # BotCommand(command="clear_quest", description="Очистить результаты опроса"),
    ]
    try:
        admins = await get_admin_ids()
        for admin in admins:
            await bot.set_my_commands(
                admin_commands, scope=BotCommandScopeChat(chat_id=admin)
            )
    except Exception as e:
        logging.error(f"Ошибка установки админских команд: {e}")
