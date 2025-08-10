from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from datetime import datetime, time
import pytz
from src.utils import haversine
from db.utils import (
    is_user_registered,
    get_user_by_telegram_id,
    add_user,
    get_today_control_by_telegram_id,
    add_today_control,
    add_not_home_distance,
    add_user_questionnaire,
)
from db.database import AsyncSessionLocal
from db.models import Questionnaire
from sqlalchemy import select
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
    await message.answer("Теперь отправьте вашу домашнюю геолокацию (гео-метку телеграма по кнопке 'Транслировать местоположение' или выберите точку на карте).")
    await state.set_state(RegisterStates.waiting_for_location)


@router.message(RegisterStates.waiting_for_location, F.location)
async def process_location(message: Message, state: FSMContext):    
    user_data = await state.get_data()
    surname = user_data["surname"]
    latitude = message.location.latitude
    longitude = message.location.longitude
    
    # сохранение пользователя в базе данных
    await add_user(message.from_user.id, surname, latitude, longitude)
    await message.answer("Регистрация завершена.")
    logging.info(
        f"Зарегистрирован новый пользователь: {message.from_user.id}, {surname}, {latitude}, {longitude}"
    )
    await state.clear()


@router.message(RegisterStates.waiting_for_location)
async def invalid_location(message: Message):
    await message.answer("Отправьте геолокацию.")


@router.message(F.location)
async def control_location(message: Message):
    # проверка, что сообщение не пересланное
    if message.forward_from or message.forward_from_chat:
        await message.answer("Отправьте новую геолокацию, а не пересланное сообщение.")
        return
    # проверка, что отправлена именно текущая геопозиция
    if not getattr(message.location, "live_period", None):
        await message.answer("Используйте кнопку 'Транслировать местоположение'.")
        return

    # проверка времени
    moscow_tz = pytz.timezone("Europe/Moscow")
    now = datetime.now(moscow_tz).time()
    if not (time(21, 40) <= now <= time(22, 10)):
        await message.answer("Отправлять геолокацию нужно только с 21:40 до 22:10.")
        logging.warning(
            f"Пользователь {message.from_user.id} попытался отправить геопозицию вне времени."
        )
        return
    
    # проверка, есть ли уже отметка пользователя
    if await get_today_control_by_telegram_id(message.from_user.id):
        await message.answer("Вы уже отправляли геолокацию сегодня. Повторная отправка невозможна.")
        logging.warning(
            f"Пользователь {message.from_user.id} попытался отправить геолокацию повторно."
        )
        return

    user = await get_user_by_telegram_id(message.from_user.id)
    
    dist = await haversine(
        user.home_latitude, user.home_longitude,
        message.location.latitude, message.location.longitude
    )
    is_home = dist <= 250
    await add_today_control(user.telegram_id, is_home)
    
    if is_home:
        logging.info(f"Пользователь {user.surname} ({message.from_user.id}) отправил геопозицию и находится дома.")
        await message.answer("Вы находитесь дома. Отметка сохранена.")
    else:
        logging.info(
            f"{user.surname} ({message.from_user.id}) находится не дома. Расстояние: {dist:.2f} м. {message.location.latitude}, {message.location.longitude}"
        )
        await add_not_home_distance(user.telegram_id, dist)
        await message.answer("Вы находитесь не дома. Отметка сохранена.")


@router.message(Command("ping"))
async def ping(message: Message):
    await message.answer("понг")


@router.callback_query(F.data.startswith("questionnaire_feeding_"))
async def questionnaire_response(data: CallbackQuery):
    user = await get_user_by_telegram_id(data.from_user.id)
    
    # проверка на повторную попытку ответа
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Questionnaire).filter_by(telegram_id=user.telegram_id)
        )
        existing_response = result.scalar_one_or_none()
        
        if existing_response:
            await data.message.answer("Вы уже ответили на опрос.")
            await data.answer()
            return
    
    will_feed = data.data == "questionnaire_feeding_yes"
    await add_user_questionnaire(user.telegram_id, user.surname, will_feed)
    if will_feed:
        logging.info(f"Пользователь {user.surname} ({user.telegram_id}) ответил на опрос: будет питаться.")
        await data.message.answer("Вы записаны на питание.")
    else:
        logging.info(f"Пользователь {user.surname} ({user.telegram_id}) ответил на опрос: не будет питаться.")
        await data.message.answer("Вы отказались от питания.")
    await data.answer()


def register_handlers(dp):
    dp.include_router(router)