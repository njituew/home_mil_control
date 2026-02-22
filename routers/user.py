from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from db.utils import (
    get_user_by_telegram_id,
    add_user_questionnaire,
    get_questionnaire_by_id,
)
from src.location import process_location
from src.exceptions import (
    ForwardedMessage,
    NotLiveLocation,
    LocationTimeOut,
    LocationAlreadyExists,
)
import logging
from src.middleware import RegistrationCheckMiddleware


router = Router()
router.message.middleware(RegistrationCheckMiddleware())
router.callback_query.middleware(RegistrationCheckMiddleware())


@router.message(F.location)
async def control_location(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает получение ежедневной геолокации от пользователя
    """

    user = await get_user_by_telegram_id(message.from_user.id)

    try:
        dist = await process_location(user, message)
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


@router.callback_query(F.data.startswith("questionnaire_answer_"))
async def questionnaire_response(data: CallbackQuery):
    """
    Обрабатывает ответ пользователя на опрос.
    Проверяет, не отвечал ли пользователь ранее на опрос. Если ответ уже был дан,
    уведомляет пользователя об этом. В противном случае сохраняет выбранный вариант
    в базу.
    """

    user = await get_user_by_telegram_id(data.from_user.id)

    # проверка на повторную попытку ответа
    if await get_questionnaire_by_id(user.telegram_id):
        logging.warning(
            f"Пользователь {user.surname} ({user.telegram_id}) попытался ответить на опрос повторно."
        )
        await data.message.answer("Вы уже ответили на опрос.")
        await data.answer()
        return

    return  # deleted feature


@router.message()
async def another_message(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    content = None

    if message.text:
        content = f"Текст: {message.text}"
    elif message.photo:
        content = "Фото"
    elif message.sticker:
        content = f"Стикер: {message.sticker.emoji or 'без emoji'}"
    elif message.document:
        content = f"Документ: {message.document.file_name}"
    elif message.voice:
        content = "Голосовое сообщение"
    elif message.video:
        content = "Видео"
    else:
        content = "Неизвестный тип сообщения"

    logging.info(
        f"Необработанное сообщение от {user.surname} "
        f"({user.telegram_id}): {content}"
    )

    await message.answer("🪖")


def register_user_handlers(dp):
    dp.include_router(router)
