from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from routers.registration import RegisterStates
from db.utils import is_user_registered, get_user_by_telegram_id
from src.utils import is_admin
import logging


class RegistrationCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if not await is_user_registered(event.from_user.id):
            state: FSMContext = data.get("state")
            if isinstance(event, Message):
                await event.answer(
                    "Пройдите процесс регистрации перед отправкой сообщения.\nВведите вашу фамилию."
                )
                await state.set_state(RegisterStates.waiting_for_surname)
            elif isinstance(event, CallbackQuery):
                await event.message.answer(
                    "Пройдите процесс регистрации перед отправкой сообщения.\nВведите вашу фамилию."
                )
                await state.set_state(RegisterStates.waiting_for_surname)
                await event.answer()
            return
        return await handler(event, data)


class AdminCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = await get_user_by_telegram_id(event.from_user.id)
        if not user:
            if isinstance(event, Message):
                await event.answer("Вы не зарегистрированы.")
            elif isinstance(event, CallbackQuery):
                await event.message.answer("Вы не зарегистрированы.")
                await event.answer()
            return
        if not await is_admin(event.from_user.id):
            if isinstance(event, Message):
                await event.answer("У вас нет прав для этой команды.")
            elif isinstance(event, CallbackQuery):
                await event.message.answer("У вас нет прав для этой команды.")
                await event.answer()
            logging.warning(
                f"Пользователь {user.surname} "
                f"({event.from_user.id}) пытался использовать админскую команду."
            )
            return
        return await handler(event, data)
