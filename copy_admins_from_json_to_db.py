from db.database import init_db
from db.utils import add_admin
import json
import asyncio


async def copy_admins_from_json_to_db(json_file_path):
    await init_db()

    # Load admin data from JSON file
    with open(json_file_path, "r") as file:
        admins_data = json.load(file)

    for admin in admins_data["admins"]:
        telegram_id = admin["chat_id"]
        await add_admin(telegram_id)
        print(f"Added admin: (Telegram ID: {telegram_id})")


if __name__ == "__main__":
    asyncio.run(copy_admins_from_json_to_db("admins.json"))
