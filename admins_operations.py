"""Утилита командной строки для управления таблицей администраторов.

Использование:
    # Добавить одного администратора по Telegram ID:
    python admins_operations.py <telegram_id>

    # Загрузить администраторов из admins.json (дубликаты пропускаются):
    python admins_operations.py

    # Загрузить из admins.json, предварительно очистив таблицу:
    python admins_operations.py --overwrite

    Формат admins.json:
        {
            "admins": [
                {"chat_id": 123456789},
                {"chat_id": 987654321}
            ]
        }

    # Удалить всех администраторов из таблицы:
    python admins_operations.py --delete
"""

import argparse
import asyncio
import json
import sys

from db.database import init_db
from db.utils import add_admin, clear_admins, get_admin_ids


async def copy_admins_from_json_to_db(
    json_file_path: str, overwrite: bool = False
) -> None:
    """Seed the admins table from a JSON file.

    Args:
        json_file_path: Path to a JSON file with an "admins" list of {"chat_id": int} objects.
        overwrite: When True, wipe the existing table before inserting.
    """
    await init_db()

    try:
        with open(json_file_path, "r") as file:
            admins_data = json.load(file)
    except FileNotFoundError:
        print(f"Ошибка: файл '{json_file_path}' не найден.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Ошибка: невалидный JSON в '{json_file_path}': {e}")
        sys.exit(1)

    json_ids: list[int] = [admin["chat_id"] for admin in admins_data["admins"]]

    if overwrite:
        deleted = await clear_admins()
        print(f"Удалено {deleted} администраторов.")
        existing_ids: set[int] = set()
    else:
        existing_ids = set(await get_admin_ids())

    added, skipped = 0, 0
    for telegram_id in json_ids:
        if telegram_id in existing_ids:
            print(f"Пропущен (уже существует): {telegram_id}")
            skipped += 1
        else:
            await add_admin(telegram_id)
            print(f"Добавлен: {telegram_id}")
            added += 1

    print(f"\nГотово. Добавлено: {added}, пропущено: {skipped}.")


async def delete_all_admins() -> None:
    """Remove every admin from the database."""
    await init_db()
    deleted = await clear_admins()
    print(f"Удалено {deleted} администраторов.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Копирование админов из JSON в БД")
    parser.add_argument(
        "admin_id",
        nargs="?",
        type=int,
        default=None,
        help="Telegram ID администратора для добавления",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Удалить всех существующих админов и записать заново",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Удалить всех администраторов из таблицы",
    )
    args = parser.parse_args()

    if args.admin_id is not None:

        async def _add_single_admin(telegram_id: int) -> None:
            await init_db()
            if telegram_id in set(await get_admin_ids()):
                print(f"Администратор {telegram_id} уже существует.")
            else:
                await add_admin(telegram_id)
                print(f"Добавлен администратор: {telegram_id}.")

        asyncio.run(_add_single_admin(args.admin_id))
    elif args.delete:
        asyncio.run(delete_all_admins())
    else:
        asyncio.run(
            copy_admins_from_json_to_db("admins.json", overwrite=args.overwrite)
        )
