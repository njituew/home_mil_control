from db.utils import (
    get_all_users,
    get_all_controls,
    get_all_alternative_locations,
)
from src.location import haversine


async def generate_report() -> str:
    users = await get_all_users()
    controls_by_id = {c.telegram_id: c for c in await get_all_controls()}

    all_alt = await get_all_alternative_locations()
    alt_by_user: dict = {}
    for alt in all_alt:
        alt_by_user.setdefault(alt.telegram_id, []).append(alt)

    at_home, not_at_home, not_checked = [], [], []

    for user in users:
        control = controls_by_id.get(user.telegram_id)
        if not control:
            not_checked.append(user.surname)
            continue

        dist = haversine(
            user.home_latitude,
            user.home_longitude,
            control.latitude,
            control.longitude,
        )

        # проверка основной (домашней) локации
        if dist <= 250:
            at_home.append(f"{user.surname} ✅")
            continue

        # проверка на предмет альтернативной локации
        found_alt = None
        for alt in alt_by_user.get(user.telegram_id, []):
            alt_dist = haversine(
                alt.latitude,
                alt.longitude,
                control.latitude,
                control.longitude,
            )
            if alt_dist <= 250:
                found_alt = alt
                break

        if found_alt:
            not_at_home.append(f"{user.surname} ({found_alt.comment})")
        else:
            not_at_home.append(f"{user.surname} ({dist/1000:.2f} км от дома)")

    text = "Отчёт:\n"
    text += "\nНе дома:\n"
    text += "\n".join(not_at_home) if not_at_home else "Все дома или все не отметились"
    text += "\n\nНе прошли опрос:\n"
    text += "\n".join(not_checked) if not_checked else "Все отметились"
    text += "\n\nДома:\n"
    text += "\n".join(at_home) if at_home else "Все не дома или все не отметились"
    return text
