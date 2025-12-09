from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from routers.registration import RegisterStates
from db.utils import is_user_registered


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
