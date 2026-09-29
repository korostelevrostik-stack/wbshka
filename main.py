import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from bot.handlers import router
from bot.scheduler import start_scheduler
from bot.scanner import scan_once
from config import config
from utils.logger import log


async def main() -> None:
    if not config.bot_token:
        raise SystemExit("BOT_TOKEN не задан в .env")

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    dp = Dispatcher()
    dp.include_router(router)

    # Фоновая задача: сканирование по расписанию
    start_scheduler(bot)

    # Первый прогон через 10 секунд после старта (для проверки)
    asyncio.create_task(_delayed_first_scan(bot))

    log.info("Бот запущен")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


async def _delayed_first_scan(bot: Bot) -> None:
    await asyncio.sleep(10)
    try:
        await scan_once(bot)
    except Exception as e:
        log.error(f"Ошибка первого скана: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Остановлено")
