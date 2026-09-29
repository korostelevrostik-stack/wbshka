from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

from config import config
from bot.scanner import scan_once
from utils.logger import log

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


def start_scheduler(bot: Bot) -> None:
    scheduler.add_job(
        scan_once,
        trigger="interval",
        minutes=config.scan_interval,
        args=[bot],
        id="scan_wb",
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    log.info(f"⏰ Планировщик запущен (каждые {config.scan_interval} мин)")
