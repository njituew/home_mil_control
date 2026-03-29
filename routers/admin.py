from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from db.utils import (
    get_all_users,
    get_user_by_telegram_id,
    get_users_by_surname,
    delete_user_by_telegram_id,
    is_admin,
    get_all_admins,
    add_admin,
    delete_admin_by_telegram_id,
    get_today_control_by_id,
    clear_today_control,
    add_alternative_location,
    delete_alternative_location,
    get_alternative_locations,
    get_all_alternative_locations,
)
from src.reports import generate_report

import logging


router = Router()


@router.message(Command("users"))
async def list_users(message: Message):
    """
    Отправляет список зарегистрированных пользователей
    """

    admin = await get_user_by_telegram_id(message.from_user.id)
    users = await get_all_users()
    if not users:
        await message.answer("Нет зарегистрированных пользователей.")
        return

    text = "Зарегистрированные пользователи:\n"
    counter = 0
    for user in users:
        counter += 1
        text += (
            f"{counter}. "
            f"Фамилия: {user.surname}, "
            f"Telegram ID: {user.telegram_id}, "
            f"Домашний адрес: {user.home_latitude}, {user.home_longitude}\n"
        )

    logging.info(
        f"Админ {admin.surname} ({admin.telegram_id}) запросил список пользователей."
    )

    await message.answer(text)


@router.message(Command("user"))
async def user_info(message: Message):
    """
    Отправляет информацию о пользователе по фамилии или telegram id
    """

    args = message.text.split()
    if len(args) != 2:
        await message.answer(
            "Отправьте команду в формате\n/user Фамилия\nили\n/user TelegramID"
        )
        return

    admin = await get_user_by_telegram_id(message.from_user.id)

    if args[1].isdigit():
        users = [await get_user_by_telegram_id(int(args[1]))]
        if not users[0]:
            await message.answer(
                "Нет зарегистрированных пользователей с таким TelegramID."
            )
            return
    else:
        users = await get_users_by_surname(args[1])
        if not users:
            await message.answer(
                "Нет зарегистрированных пользователей с такой фамилией."
            )
            return

    text = ""
    counter = 0
    for user in users:
        counter += 1
        text += (
            f"{counter}. "
            f"Фамилия: {user.surname}, "
            f"Telegram ID: {user.telegram_id}, "
            f"Домашний адрес: {user.home_latitude}, {user.home_longitude}\n"
        )

    logging.info(
        f"Админ {admin.surname} ({admin.telegram_id}) запросил информацию по пользователю {args[1]}."
    )

    await message.answer(text)


@router.message(Command("delete"))
async def delete_user(message: Message):
    """
    Удаляет пользователя по telegram id
    """

    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Используйте команду в формате: /delete <telegram_id>")
        return

    admin = await get_user_by_telegram_id(message.from_user.id)
    deleted_user = await get_user_by_telegram_id(int(args[1]))

    if not deleted_user:
        logging.warning(
            f"Админ {admin.surname} ({admin.telegram_id}) "
            f"попытался удалить несуществующего пользователя с Telegram ID {args[1]}."
        )
        await message.answer(
            f"❌ Пользователь с Telegram ID {args[1]} не найден в базе."
        )
        return

    await delete_user_by_telegram_id(deleted_user.telegram_id)

    logging.info(
        f"Админ {admin.surname} ({admin.telegram_id}) "
        f"удалил пользователя {deleted_user.surname} ({deleted_user.telegram_id})."
    )

    await message.answer(
        f"🗑️ Пользователь {deleted_user.surname} ({deleted_user.telegram_id}) удалён."
    )


@router.message(Command("clear"))
async def clear_control(message: Message):
    """
    Очищает таблицу с ежедневными отметками локаций пользователей
    """

    await clear_today_control()
    admin = await get_user_by_telegram_id(message.from_user.id)
    logging.info(
        f"Админ {admin.surname} ({admin.telegram_id}) очистил таблицу TodayControl."
    )
    await message.answer("Сегодняшние отметки успешно удалены.")


@router.message(Command("control"))
async def show_control_report(message: Message):
    """
    Отправляет отчёт по локациям
    """

    report = await generate_report()
    admin = await get_user_by_telegram_id(message.from_user.id)
    logging.info(
        f"Админ {admin.surname} ({admin.telegram_id}) запросил отчёт по TodayControl."
    )
    await message.answer(report)


@router.message(Command("where_is"))
async def where_is_user(message: Message):
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Используйте формат: /where_is <telegram_id>")
        return

    telegram_id = int(args[1])
    admin = await get_user_by_telegram_id(message.from_user.id)
    user = await get_user_by_telegram_id(telegram_id)

    if not user:
        logging.warning(
            f"Админ {admin.surname} ({admin.telegram_id}) "
            f"запросил локацию несуществующего пользователя {telegram_id}."
        )
        await message.answer(
            f"❌ Пользователь с Telegram ID {telegram_id} не найден в базе."
        )
        return

    control = await get_today_control_by_id(user.telegram_id)
    if not control:
        await message.answer(
            f"❌ Пользователь {user.surname} ещё не отправил локацию сегодня."
        )
        return

    logging.info(
        f"Админ {admin.surname} ({admin.telegram_id}) запросил локацию "
        f"пользователя {user.surname} ({user.telegram_id})."
    )

    await message.answer(
        f"Пользователь {user.surname} отправил локацию\n{control.latitude}, {control.longitude}"
    )


@router.message(Command("add_alt"))
async def add_alt_location(message: Message):
    """
    Добавляет альтернативную локацию для пользователя
    """

    args = message.text.split(maxsplit=4)
    if len(args) < 4:
        await message.answer(
            "Используй формат:\n/add_alt <telegram_id> <latitude> <longitude> [комментарий]"
        )
        return

    try:
        telegram_id = int(args[1])
        latitude = float(args[2])
        longitude = float(args[3])
        comment = " ".join(args[4:])
    except ValueError:
        await message.answer("Некорректные параметры. Проверьте формат чисел.")
        return

    admin = await get_user_by_telegram_id(message.from_user.id)
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        logging.warning(
            f"Админ {admin.surname} ({admin.telegram_id}) "
            f"попытался добавить локацию несуществующему пользователю {telegram_id}."
        )
        await message.answer(
            f"❌ Пользователь с Telegram ID {telegram_id} не найден в базе."
        )
        return

    await add_alternative_location(telegram_id, latitude, longitude, comment)

    logging.info(
        f"Админ {admin.surname} ({admin.telegram_id}) "
        f"добавил альтернативную локацию для пользователя {user.surname} ({user.telegram_id})."
    )
    await message.answer(
        f"✅ Альтернативная локация добавлена для {user.surname} ({user.telegram_id})"
    )


@router.message(Command("user_alt"))
async def list_alt_locations(message: Message):
    """
    Отправляет альтернативные локации пользователя
    """

    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Используйте формат: /user_alt <telegram_id>")
        return

    telegram_id = int(args[1])
    locations = await get_alternative_locations(telegram_id)
    if not locations:
        await message.answer("У этого пользователя нет альтернативных локаций.")
        return

    text = "Альтернативные локации:\n"
    for loc in locations:
        text += (
            f"ID: {loc.id} | "
            f"Lat: {loc.latitude}, Lon: {loc.longitude} "
            f"| Комментарий: {loc.comment or '-'}\n"
        )

    admin = await get_user_by_telegram_id(message.from_user.id)
    user = await get_user_by_telegram_id(telegram_id)
    logging.info(
        f"Админ {admin.surname} ({admin.telegram_id}) "
        f"запросил альтернативные локации пользователя {user.surname} ({user.telegram_id})."
    )
    await message.answer(text)


@router.message(Command("all_alt"))
async def list_all_alt_locations(message: Message):
    """
    Отправляет все существующие альтернативные локации
    """

    admin = await get_user_by_telegram_id(message.from_user.id)
    logging.info(
        f"Админ {admin.surname} ({admin.telegram_id}) "
        f"запросил все альтернативные локации."
    )

    all_locations = await get_all_alternative_locations()
    if not all_locations:
        await message.answer("В базе нет альтернативных локаций.")
        return

    # группируем локации по пользователям в памяти
    locations_by_user: dict = {}
    for loc in all_locations:
        locations_by_user.setdefault(loc.telegram_id, []).append(loc)

    # загружаем данные всех пользователей одним запросом
    all_users = await get_all_users()
    users_by_id = {u.telegram_id: u for u in all_users}

    text = "Альтернативные локации:\n"
    user_counter = 0
    for user_id, locs in locations_by_user.items():
        user_counter += 1
        user = users_by_id.get(user_id)
        if user:
            text += f"{user_counter}. {user.surname} ({user_id}):\n"
        else:
            text += f"{user_counter}. [удалённый пользователь] ({user_id}):\n"
        for loc_counter, loc in enumerate(locs, start=1):
            text += (
                f"\t\t\t{loc_counter}) "
                f"ID: {loc.id} | "
                f"Lat: {loc.latitude}, Lon: {loc.longitude} | "
                f"{loc.comment or '-'}\n"
            )

    await message.answer(text)


@router.message(Command("del_alt"))
async def delete_alt_location_cmd(message: Message):
    """
    Удаляет альтернативную локацию по ID локации
    """

    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Используйте формат: /del_alt <location_id>")
        return

    location_id = int(args[1])
    deleted = await delete_alternative_location(location_id)

    admin = await get_user_by_telegram_id(message.from_user.id)

    if not deleted:
        logging.warning(
            f"Админ {admin.surname} ({admin.telegram_id}) попытался удалить "
            f"несуществующую альтернативную локацию {location_id}."
        )
        await message.answer(
            f"❌ Альтернативная локация с ID {location_id} не найдена."
        )
        return

    logging.info(
        f"Админ {admin.surname} ({admin.telegram_id}) удалил альтернативную локацию {location_id}."
    )
    await message.answer(f"🗑️ Альтернативная локация {location_id} удалена.")


@router.message(Command("ping_all"))
async def ping_all(message: Message):
    """
    Отправляет сообщение всем пользователям
    """

    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].strip():
        await message.answer("Используйте команду в формате: /ping_all {текст}")
        return

    text = args[1].strip()
    users = await get_all_users()
    count = 0
    for user in users:
        try:
            await message.bot.send_message(user.telegram_id, text)
            count += 1
        except Exception as e:
            logging.error(
                f"Ошибка отправки сообщения пользователю {user.telegram_id}: {e}"
            )

    admin = await get_user_by_telegram_id(message.from_user.id)
    logging.info(
        f"Админ {admin.surname} ({admin.telegram_id}) отправил массовое сообщение '{text}' {count} пользователям."
    )
    await message.answer(f"Сообщение отправлено {count} пользователям.")


@router.message(Command("admins"))
async def list_admins(message: Message):
    """
    Отправляет список администраторов
    """
    admin = await get_user_by_telegram_id(message.from_user.id)
    admins = await get_all_admins()

    # загружаем всех пользователей, чтобы не делать запрос в цикле
    all_users = await get_all_users()
    users_by_id = {u.telegram_id: u for u in all_users}

    text = "Администраторы:\n"
    counter = 0
    for a in admins:
        counter += 1
        user_admin = users_by_id.get(a.telegram_id)
        if not user_admin:
            text += (
                f"{counter}. "
                f"Незарегистрированный админ. "
                f"Telegram ID: {a.telegram_id}\n"
            )
        else:
            text += (
                f"{counter}. "
                f"Фамилия: {user_admin.surname}, "
                f"Telegram ID: {user_admin.telegram_id}\n"
            )

    logging.info(
        f"Админ {admin.surname} ({admin.telegram_id}) запросил список администраторов."
    )

    await message.answer(text)


@router.message(Command("add_admin"))
async def add_admin_cmd(message: Message):
    """
    Добавляет администратора по telegram id
    """

    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Используйте команду в формате: /add_admin <telegram_id>")
        return

    admin = await get_user_by_telegram_id(message.from_user.id)
    new_admin_id = int(args[1])

    if await is_admin(new_admin_id):
        logging.warning(
            f"Админ {admin.surname} ({admin.telegram_id}) попытался добавить "
            f"админа {new_admin_id}, который уже является админом."
        )
        await message.answer(
            f"Пользователь с Telegram ID {new_admin_id} уже является администратором."
        )
        return

    await add_admin(new_admin_id)

    logging.info(
        f"Админ {admin.surname} ({admin.telegram_id}) "
        f"добавил нового администратора {new_admin_id}."
    )

    await message.answer(f"✅ Пользователь {new_admin_id} теперь администратор.")


@router.message(Command("delete_admin"))
async def delete_admin_cmd(message: Message):
    """
    Удаляет администратора по telegram id
    """

    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer(
            "Используйте команду в формате: /delete_admin <telegram_id>"
        )
        return

    admin = await get_user_by_telegram_id(message.from_user.id)
    deleted_admin_id = int(args[1])

    if not await is_admin(deleted_admin_id):
        logging.warning(
            f"Админ {admin.surname} ({admin.telegram_id}) попытался удалить "
            f"админа {deleted_admin_id}, который не является админом."
        )
        await message.answer(
            f"Пользователь с Telegram ID {deleted_admin_id} не является администратором."
        )
        return

    await delete_admin_by_telegram_id(deleted_admin_id)

    logging.info(
        f"Админ {admin.surname} ({admin.telegram_id}) "
        f"удалил администратора {deleted_admin_id}."
    )

    await message.answer(
        f"✅ Пользователь {deleted_admin_id} удалён из администраторов."
    )


def register_admin_handlers(dp, admin_middleware):
    router.message.middleware(admin_middleware)
    dp.include_router(router)
