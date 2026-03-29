import logging

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from routers.registration import RegisterStates
from db.utils import is_user_registered, is_admin, get_user_by_telegram_id


class RegistrationCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if not await is_user_registered(event.from_user.id):
            state: FSMContext = data.get("state")
            current_state = await state.get_state()
            if current_state in RegisterStates.__all_states_names__:
                return await handler(event, data)
            if await is_admin(event.from_user.id):
                return await handler(event, data)

            await state.set_state(RegisterStates.waiting_for_surname)
            text = "Пройдите процесс регистрации перед отправкой сообщения.\nВведите вашу фамилию."

            if isinstance(event, Message):
                await event.answer(text)
            elif isinstance(event, CallbackQuery):
                await event.message.answer(text)
                await event.answer()
            return
        return await handler(event, data)


class AdminCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if not await is_admin(event.from_user.id):
            user = await get_user_by_telegram_id(event.from_user.id)
            if isinstance(event, Message):
                await event.answer("У вас нет прав для этой команды.")
            elif isinstance(event, CallbackQuery):
                await event.message.answer("У вас нет прав для этой команды.")
                await event.answer()
            logging.warning(
                f"Пользователь {user.surname if user else event.from_user.id} "
                f"({event.from_user.id}) пытался использовать админскую команду."
            )
            return
        return await handler(event, data)
