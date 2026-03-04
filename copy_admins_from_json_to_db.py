from db.database import init_db
from db.utils import add_admin, get_admin_ids, delete_admin_by_telegram_id, get_all_admins
import json
import asyncio
import argparse


async def copy_admins_from_json_to_db(json_file_path: str, overwrite: bool = False):
    await init_db()

    with open(json_file_path, "r") as file:
        admins_data = json.load(file)

    json_ids = [admin["chat_id"] for admin in admins_data["admins"]]

    if overwrite:
        existing_admins = await get_all_admins()
        for admin in existing_admins:
            await delete_admin_by_telegram_id(admin.telegram_id)
        print(f"Удалено {len(existing_admins)} администраторов.")

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Копирование админов из JSON в БД")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Удалить всех существующих админов и записать заново",
    )
    args = parser.parse_args()

    asyncio.run(copy_admins_from_json_to_db("admins.json", overwrite=args.overwrite))
