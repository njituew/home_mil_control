from dotenv import load_dotenv
import os


def get_bot_token():
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN is not set in the environment variables.")
    return bot_token

def get_database_dsn():
    load_dotenv()
    database_dsn = os.getenv("DATABASE_DSN")
    if not database_dsn:
        raise ValueError("DATABASE_DSN is not set in the environment variables.")
    return database_dsn