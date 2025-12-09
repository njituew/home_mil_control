from db.utils import (
    get_all_users,
    get_all_controls,
    get_alternative_locations,
    get_all_questionnaire,
)
from src.location import haversine


async def generate_report() -> str:
    users = await get_all_users()
    controls_by_id = {c.telegram_id: c for c in await get_all_controls()}

    at_home, not_at_home, not_checked = [], [], []

    for user in users:
        control = controls_by_id.get(user.telegram_id)
        if not control:
            not_checked.append(user.surname)
            continue

        dist = await haversine(
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
        alt_locations = await get_alternative_locations(user.telegram_id)
        found_alt = None

        for alt in alt_locations:
            alt_dist = await haversine(
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


async def generate_report_quest() -> str:
    users = await get_all_users()

    questionnaires = await get_all_questionnaire()
    questionnaires_by_id = {q.telegram_id: q for q in questionnaires}

    will_feed_users = [
        f"{user.surname} {'✅' if questionnaires_by_id[user.telegram_id].will_feed else '❌'}"
        for user in users
        if user.telegram_id in questionnaires_by_id
    ]

    not_answered = [
        user.surname for user in users if user.telegram_id not in questionnaires_by_id
    ]

    text = "Отчёт по опросу:\n"
    text += "\nРезультаты опроса:\n"
    text += "\n".join(will_feed_users) if will_feed_users else "Никто не прошёл опрос"
    text += "\n\nНе прошли опрос:\n"
    text += "\n".join(not_answered) if not_answered else "Все отметились"
    return text
