from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from src.utils import haversine
from src.config import is_test_mode
from db.utils import (
    is_user_registered,
    get_user_by_telegram_id,
    get_today_control_by_id,
    add_today_control,
    add_user_questionnaire,
    get_questionnaire_by_id,
)

from routers.registration import RegisterStates

from datetime import datetime, time
import pytz
import logging


router = Router()


@router.message(F.location)
async def control_location(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает получение геолокации от пользователя.

    При успешных проверках вычисляет расстояние от дома пользователя до текущего местоположения
    и сохраняет отметку. Отправляет пользователю соответствующее уведомление.

    Args:
        message (Message): Объект входящего сообщения с геолокацией.
        state (FSMContext): Контекст состояния машины состояний (для начала процесса регистрации).

    Returns:
        None
    """

    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        return

    # проверка что пользователь есть в базе
    if not await is_user_registered(message.from_user.id):
        # начало регистрации
        await message.answer(
            "Для пользования ботом пройдите процесс регистрации.\nВведите вашу фамилию."
        )
        await state.set_state(RegisterStates.waiting_for_surname)
        return

    # проверка, что сообщение не пересланное
    if message.forward_from or message.forward_from_chat:
        logging.warning(
            f"Пользователь {user.surname} ({user.telegram_id}) попытался переслать локацию."
        )
        await message.answer(
            "❌ Самый хитрый? Отправь новую геолокацию, а не пересланное сообщение."
        )
        return

    # проверка, что отправлена именно текущая геопозиция
    if not is_test_mode():
        if not getattr(message.location, "live_period", None):
            logging.warning(
                f"Пользователь {user.surname} ({user.telegram_id}) попытался отправить точку на карте."
            )
            await message.answer(
                "❌ Используйте кнопку 'Транслировать местоположение'."
            )
            return
    else:
        logging.info(f"Проверка live пропущена для {user.telegram_id}")

    # проверка времени
    if not is_test_mode():
        moscow_tz = pytz.timezone("Europe/Moscow")
        now = datetime.now(moscow_tz).time()
        if not (time(21, 40) <= now <= time(22, 10)):
            await message.answer(
                "❌ Геолокация не сохранена. Отправлять геолокацию нужно только с 21:40 до 22:10."
            )
            logging.warning(
                f"Пользователь {user.surname} ({user.telegram_id}) попытался отправить геопозицию вне времени."
            )
            return
    else:
        logging.info(f"Проверка времени пропущена для {user.telegram_id}")

    # проверка, есть ли уже отметка пользователя
    if await get_today_control_by_id(message.from_user.id):
        await message.answer(
            "❌ Вы уже отправляли геолокацию сегодня. Повторная отправка невозможна."
        )
        logging.warning(
            f"Пользователь {user.surname} ({user.telegram_id}) попытался отправить геолокацию повторно."
        )
        return

    # обработка новой локации
    await add_today_control(
        user.telegram_id,
        message.location.latitude,
        message.location.longitude,
    )

    dist = await haversine(
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
            f"Пользователь {user.surname} ({user.telegram_id}) находится не дома. "
            f"Расстояние: {dist:.2f} м. {message.location.latitude}, {message.location.longitude}"
        )
        await message.answer("Вы находитесь НЕ дома. Отметка сохранена.")


@router.message(Command("ping"))
async def ping(message: Message):
    """
    Проверка пульса.

    Args:
        message (Message): Объект входящего сообщения.
    """
    await message.answer("понг")


@router.callback_query(F.data.startswith("questionnaire_feeding_"))
async def questionnaire_response(data: CallbackQuery):
    """
    Обрабатывает ответ пользователя на опрос.

    Проверяет, не отвечал ли пользователь ранее на опрос. Если ответ уже был дан,
    уведомляет пользователя об этом. В противном случае сохраняет выбранный вариант
    в базу.

    Args:
        data (CallbackQuery): Объект обратного вызова кнопки.

    Returns:
        None: Функция ничего не возвращает. Отправляет сообщение пользователю и подтверждает
              нажатие кнопки.

    Logging:
        - Записывает в лог:
            - попытку повторного ответа;
            - успешный ответ (с указанием выбора: будет или не будет питаться).
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

    will_feed = data.data == "questionnaire_feeding_yes"
    await add_user_questionnaire(user.telegram_id, user.surname, will_feed)
    if will_feed:
        logging.info(
            f"Пользователь {user.surname} ({user.telegram_id}) ответил на опрос: будет питаться."
        )
        await data.message.answer("Вы записаны на питание.")
    else:
        logging.info(
            f"Пользователь {user.surname} ({user.telegram_id}) ответил на опрос: не будет питаться."
        )
        await data.message.answer("Вы отказались от питания.")
    await data.answer()


def register_user_handlers(dp):
    dp.include_router(router)
