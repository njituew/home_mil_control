from dotenv import load_dotenv
import os
import logging


def get_bot_token() -> str:
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN is not set in the environment variables.")
    return bot_token


def get_database_dsn() -> str:
    load_dotenv()
    database_dsn = os.getenv("DATABASE_DSN")
    if not database_dsn:
        raise ValueError("DATABASE_DSN is not set in the environment variables.")
    return database_dsn


def get_logs_path() -> str:
    load_dotenv()
    logs_path = os.getenv("LOGS_PATH")
    return logs_path


def init_logging():
    file_path = get_logs_path()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(file_path, encoding="utf-8", mode="a"),
        ],
    )
    return logging


def is_test_mode() -> bool:
    return os.getenv("TEST_MODE", "false").lower() == "true"
