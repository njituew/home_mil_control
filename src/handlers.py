from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from db.models import User
from db.database import AsyncSessionLocal
from sqlalchemy import select
from datetime import datetime, time, date
from db.models import TodayControl
from src.utils import haversine
import pytz


router = Router()


# стейты регистрации
class RegisterStates(StatesGroup):
    waiting_for_surname = State()
    waiting_for_location = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    # проверка регистрации пользователя
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        if user:
            await message.answer("Вы уже зарегистрированы!")
            await state.clear()
            return
    # начало регистрации
    await message.answer("Введите вашу фамилию.")
    await state.set_state(RegisterStates.waiting_for_surname)


@router.message(RegisterStates.waiting_for_surname)
async def process_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await message.answer("Теперь отправьте вашу домашнюю геолокацию (гео-метку телеграма по кнопке 'Транслировать местоположение').")
    await state.set_state(RegisterStates.waiting_for_location)


@router.message(RegisterStates.waiting_for_location, F.location)
async def process_location(message: Message, state: FSMContext):
    # Проверка, что сообщение не пересланное
    if message.forward_from or message.forward_from_chat:
        await message.answer("Пожалуйста, отправьте новую геолокацию, а не пересланное сообщение.")
        return
    # Проверка, что отправлена именно текущая геопозиция
    if not getattr(message.location, "live_period", None):
        await message.answer("Используйте кнопку 'Транслировать местоположение'.")
        return
    
    user_data = await state.get_data()
    surname = user_data["surname"]
    latitude = message.location.latitude
    longitude = message.location.longitude
    
    # сохранение пользователя в базе данных
    async with AsyncSessionLocal() as session:
        user = User(
            telegram_id=message.from_user.id,
            surname=surname,
            home_latitude=latitude,
            home_longitude=longitude
        )
        session.add(user)
        await session.commit()
    
    await message.answer("Регистрация завершена. Ваши данные сохранены.")
    await state.clear()


@router.message(RegisterStates.waiting_for_location)
async def invalid_location(message: Message):
    await message.answer("Пожалуйста, отправьте геолокацию.")


@router.message(F.location)
async def control_location(message: Message, state: FSMContext):
    # Не реагировать, если пользователь в процессе регистрации
    current_state = await state.get_state()
    if current_state in [
        RegisterStates.waiting_for_surname.state,
        RegisterStates.waiting_for_location.state
    ]:
        return
    
    # Проверка, что сообщение не пересланное
    if message.forward_from or message.forward_from_chat:
        await message.answer("Пожалуйста, отправьте новую геолокацию, а не пересланное сообщение.")
        return
    # Проверка, что отправлена именно текущая геопозиция
    if not getattr(message.location, "live_period", None):
        await message.answer("Используйте кнопку 'Транслировать местоположение'.")
        return

    # Проверка времени по Москве
    moscow_tz = pytz.timezone("Europe/Moscow")
    now = datetime.now(moscow_tz).time()
    if not (time(21, 40) <= now <= time(22, 20)):
        await message.answer("Отправлять геолокацию нужно только с 21:40 до 22:20.")
        return

    async with AsyncSessionLocal() as session:
        # Проверяем, есть ли уже отметка пользователя
        result = await session.execute(
            select(TodayControl).where(TodayControl.telegram_id == message.from_user.id)
        )
        control = result.scalar_one_or_none()
        if control:
            await message.answer("Вы уже отправляли геолокацию сегодня. Повторная отправка невозможна.")
            return

        # Получаем пользователя для координат дома
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        if not user:
            await message.answer("Сначала зарегистрируйтесь с помощью /start.")
            return

        dist = haversine(
            user.home_latitude, user.home_longitude,
            message.location.latitude, message.location.longitude
        )
        is_home = dist <= 250

        control = TodayControl(telegram_id=user.telegram_id, is_home=is_home)
        session.add(control)
        await session.commit()

        if is_home:
            await message.answer("Вы находитесь дома. Отметка сохранена.")
        else:
            await message.answer("Вы находитесь не дома. Отметка сохранена.")


def register_handlers(dp):
    dp.include_router(router)