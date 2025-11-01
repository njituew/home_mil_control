from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from db.utils import (
    is_user_registered,
    add_user,
)
import logging


router = Router()


# стейты регистрации
class RegisterStates(StatesGroup):
    waiting_for_surname = State()
    waiting_for_location = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    # проверка регистрации пользователя
    if await is_user_registered(message.from_user.id):
        await message.answer("Вы уже зарегистрированы!")
        await state.clear()
        return
    # начало регистрации
    await message.answer("Введите вашу фамилию.")
    await state.set_state(RegisterStates.waiting_for_surname)


@router.message(RegisterStates.waiting_for_surname)
async def process_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await message.answer(
        "Теперь отправьте вашу домашнюю геолокацию (гео-метку телеграма по кнопке 'Транслировать местоположение' или выберите точку на карте)."
    )
    await state.set_state(RegisterStates.waiting_for_location)


@router.message(RegisterStates.waiting_for_location, F.location)
async def process_location(message: Message, state: FSMContext):
    await state.update_data(
        latitude=message.location.latitude, longitude=message.location.longitude
    )
    await save_user(message, state)


async def save_user(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await add_user(message.from_user.id, user_data["surname"], user_data["latitude"], user_data["longitude"])
    await message.answer("Регистрация завершена.")
    logging.info(
        f'Зарегистрирован новый пользователь: {message.from_user.id}, {user_data["surname"]}, {user_data["latitude"]}, {user_data["longitude"]}'
    )

    await state.clear()


@router.message(RegisterStates.waiting_for_location)
async def invalid_location(message: Message):
    await message.answer("Отправьте геолокацию.")


def register_registration_handlers(dp):
    dp.include_router(router)
