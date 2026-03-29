from math import sin, cos, asin, sqrt, radians
from db.models import User
from db.utils import get_today_control_by_id
from datetime import datetime, time

import logging
from src.config import is_test_mode
from src.exceptions import (
    ForwardedMessage,
    NotLiveLocation,
    LocationTimeOut,
    LocationAlreadyExists,
)
from aiogram.types import Message


async def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Возвращает расстояние между двумя точками (в метрах) по координатам.
    """
    R = 6371000  # Радиус Земли в метрах
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


async def validate_location(user: User, message: Message) -> None:
    """Проверка локации на валидность

    Raises:
        ForwardedMessage: сообщение переслано (не допускается)
        NotLiveLocation: отправлена не трансляция геопозиции, а точка на карте
        LocationTimeOut: сообщение отправлено не в отведённое время
        LocationAlreadyExists: пользователь уже отправлял локацию сегодня
    """
    if not is_test_mode():
        # проверка, что сообщение не пересланное
        if message.forward_from or message.forward_from_chat:
            logging.warning(
                f"Пользователь {user.surname} ({user.telegram_id}) попытался переслать локацию."
            )
            raise ForwardedMessage

        # проверка, что отправлена трансляция геопозиции
        if not getattr(message.location, "live_period", None):
            logging.warning(
                f"Пользователь {user.surname} ({user.telegram_id}) попытался отправить точку на карте."
            )
            raise NotLiveLocation

        # проверка времени
        now = datetime.now().time()
        if not (time(21, 40) <= now <= time(22, 10)):
            logging.warning(
                f"Пользователь {user.surname} ({user.telegram_id}) попытался отправить геопозицию вне времени."
            )
            raise LocationTimeOut
    else:
        logging.info(f"Проверка пропущена для {user.telegram_id}")

    # проверка, есть ли уже отметка пользователя
    if await get_today_control_by_id(message.from_user.id):
        logging.warning(
            f"Пользователь {user.surname} ({user.telegram_id}) попытался отправить геолокацию повторно."
        )
        raise LocationAlreadyExists
