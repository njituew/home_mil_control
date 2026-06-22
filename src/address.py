import logging

import httpx

from src.config import get_email_for_API


async def get_address_by_coordinates(lat: float, lon: float) -> str:
    """Получает примерный адрес по координатам. Используется API nominatim.org

    Args:
        lat (float): Широта
        lon (float): Долгота

    Returns:
        str: Адрес или fallback-строка при ошибке
    """

    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "accept-language": "ru",
    }
    headers = {"User-Agent": f"HomeMilControlBot/1.0 ({get_email_for_API()})"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url="https://nominatim.openstreetmap.org/reverse",
                params=params,
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as e:
        logging.error(
            f"Nominatim вернул ошибку {e.response.status_code} для ({lat}, {lon})"
        )
        return "адрес не определён"
    except httpx.RequestError as e:
        logging.error(f"Ошибка соединения с Nominatim для ({lat}, {lon}): {e}")
        return "адрес не определён"

    address = data.get("address", {})
    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality", "")
    )
    road = address.get("road", "")
    house = address.get("house_number", "")

    parts = [p for p in [city, road, house] if p]
    return ", ".join(parts) if parts else "адрес не определён"
