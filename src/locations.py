from db.utils import add_today_control
from math import radians, cos, sin, asin, sqrt


async def haversine(lat1, lon1, lat2, lon2) -> int:
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


async def process_loc(user, latitude, longitude) -> int:
    await add_today_control(user.telegram_id, latitude, longitude)
    dist = await haversine(
        user.home_latitude,
        user.home_longitude,
        latitude,
        longitude,
    )
    return dist
