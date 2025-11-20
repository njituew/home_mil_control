from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from src.notification import (
    send_reminder,
    send_daily_report,
    send_last_chance,
)
import pytz
from db.utils import clear_today_control


def init_scheduler(bot):
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Europe/Moscow"))
    scheduler.add_job(
        clear_today_control,
        CronTrigger(hour=19, minute=30),
        id="clear_today_control",
        replace_existing=True,
    )
    scheduler.add_job(
        send_reminder,
        CronTrigger(hour=19, minute=40),
        args=[bot],
        id="send_reminder",
        replace_existing=True,
    )
    scheduler.add_job(
        send_last_chance,
        CronTrigger(hour=20, minute=5),
        args=[bot],
        id="send_last_chance",
        replace_existing=True,
    )
    scheduler.add_job(
        send_daily_report,
        CronTrigger(hour=20, minute=10),
        args=[bot],
        id="send_daily_report",
        replace_existing=True,
    )

    return scheduler
