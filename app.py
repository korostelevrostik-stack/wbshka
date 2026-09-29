import asyncio
import os
import threading
from aiohttp import web

# Импортируем вашу главную функцию бота
from main import main as bot_main


def start_bot():
    """Запускает бота в отдельном потоке."""
    asyncio.run(bot_main())


async def health(request):
    """Эндпоинт для проверки работоспособности (для UptimeRobot)."""
    return web.Response(text="OK")


async def index(request):
    return web.Response(text="WB Catalog Bot is running")


async def run_web():
    """Запускает веб-сервер на порту, который требует Render."""
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/health", health)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render передаёт порт через переменную окружения PORT
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server started on port {port}")
    # Бесконечно ждём, чтобы сервер не выключался
    await asyncio.Event().wait()


if __name__ == "__main__":
    # 1. Запускаем Telegram-бота в фоне
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    # 2. Запускаем веб-сервер в основном потоке
    asyncio.run(run_web())
