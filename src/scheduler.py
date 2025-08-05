from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from src.notification import (
    send_reminder,
    send_daily_report,
    send_last_chance,
)
import pytz
from db.utils import clear_data


def init_scheduler(bot):
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Europe/Moscow"))
    scheduler.add_job(
        send_reminder,
        CronTrigger(hour=18, minute=40),
        args=[bot],
        id="send_reminder",
        replace_existing=True
    )
    scheduler.add_job(
        send_last_chance,
        CronTrigger(hour=19, minute=5),
        args=[bot],
        id="send_last_chance",
        replace_existing=True
    )
    scheduler.add_job(
        send_daily_report,
        CronTrigger(hour=19, minute=12),
        args=[bot],
        id="send_daily_report",
        replace_existing=True
    )
    scheduler.add_job(
        clear_data,
        CronTrigger(hour=19, minute=15),
        id="clear_data",
        replace_existing=True
    )
    
    return scheduler