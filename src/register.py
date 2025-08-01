from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from db.models import User
from db.database import AsyncSessionLocal

router = Router()

# Определение состояний для регистрации
class RegisterStates(StatesGroup):
    waiting_for_surname = State()
    waiting_for_location = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Добро пожаловать! Давайте зарегистрируемся. Введите вашу фамилию.")
    await state.set_state(RegisterStates.waiting_for_surname)

@router.message(RegisterStates.waiting_for_surname)
async def process_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await message.answer("Отлично! Теперь отправьте вашу домашнюю геолокацию.")
    await state.set_state(RegisterStates.waiting_for_location)

@router.message(RegisterStates.waiting_for_location, F.location)
async def process_location(message: Message, state: FSMContext):
    user_data = await state.get_data()
    surname = user_data["surname"]
    latitude = message.location.latitude
    longitude = message.location.longitude
    
    # Сохранение данных в базу асинхронно
    async with AsyncSessionLocal() as session:
        user = User(
            telegram_id=message.from_user.id,
            surname=surname,
            home_latitude=latitude,
            home_longitude=longitude
        )
        session.add(user)
        await session.commit()
    
    await message.answer("Регистрация завершена! Ваши данные сохранены.")
    await state.clear()

@router.message(RegisterStates.waiting_for_location)
async def invalid_location(message: Message):
    await message.answer("Пожалуйста, отправьте геолокацию.")

def register_handlers(dp):
    dp.include_router(router)