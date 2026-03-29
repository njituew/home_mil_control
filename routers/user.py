from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from db.utils import (
    get_user_by_telegram_id,
    add_today_control,
)
from src.location import haversine, validate_location
from src.exceptions import (
    ForwardedMessage,
    NotLiveLocation,
    LocationTimeOut,
    LocationAlreadyExists,
)
import logging


router = Router()


@router.message(F.location)
async def control_location(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает получение ежедневной геолокации от пользователя
    """

    user = await get_user_by_telegram_id(message.from_user.id)

    try:
        await validate_location(user, message)
    except ForwardedMessage:
        await message.answer(
            "❌ Самый хитрый? Отправь новую геолокацию, а не пересланное сообщение."
        )
        return
    except NotLiveLocation:
        await message.answer("❌ Используйте кнопку 'Транслировать местоположение'.")
        return
    except LocationTimeOut:
        await message.answer(
            "❌ Геолокация не сохранена. Отправлять геолокацию нужно только с 21:40 до 22:10."
        )
        return
    except LocationAlreadyExists:
        await message.answer(
            "❌ Вы уже отправляли геолокацию сегодня. Повторная отправка невозможна."
        )
        return

    await add_today_control(
        user.telegram_id,
        message.location.latitude,
        message.location.longitude,
    )

    dist = haversine(
        user.home_latitude,
        user.home_longitude,
        message.location.latitude,
        message.location.longitude,
    )

    if dist <= 250:
        logging.info(
            f"Пользователь {user.surname} ({user.telegram_id}) отправил геопозицию и находится дома."
        )
        await message.answer("Вы находитесь дома. Отметка сохранена.")
    else:
        logging.info(
            f"Пользователь {user.surname} ({user.telegram_id}) отправил геопозицию и находится не дома. "
            f"Расстояние: {dist:.2f} м. {message.location.latitude}, {message.location.longitude}"
        )
        await message.answer("Вы находитесь НЕ дома. Отметка сохранена.")


@router.message(Command("ping"))
async def ping(message: Message):
    """
    Проверка пульса.
    """
    user = await get_user_by_telegram_id(message.from_user.id)
    logging.info(f"Пользователь {user.surname} ({user.telegram_id}) использовал /ping.")
    await message.answer("понг")


@router.message(Command("info"))
async def project_info(message: Message):
    """
    GitHub 🥷
    """
    user = await get_user_by_telegram_id(message.from_user.id)
    logging.info(f"Пользователь {user.surname} ({user.telegram_id}) использовал /info.")
    await message.answer("GitHub:\nhttps://github.com/njituew/home_mil_control/")


@router.message()
async def another_message(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    user_label = (
        f"{user.surname} ({user.telegram_id})" if user else str(message.from_user.id)
    )
    logging.info(
        f"Необработанное сообщение от {user_label}: тип {message.content_type}"
    )
    await message.answer("🪖")


def register_user_handlers(dp):
    dp.include_router(router)
