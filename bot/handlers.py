from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import config
from db.repository import repo
from utils.logger import log

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    repo.add_user(message.from_user.id)
    await message.answer(
        "Привет! Я бот для публикации товаров с Wildberries в канал.\n\n"
        "Команды:\n"
        "/stats — статистика\n"
        "/test &lt;nm_id&gt; — протестировать карточку товара\n"
        "/id — показать id канала из настроек",
        parse_mode="HTML",
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    s = repo.stats()
    await message.answer(
        f"📊 Опубликовано товаров: {s['posted']}\n"
        f"👥 Пользователей: {s['users']}"
    )


@router.message(Command("id"))
async def cmd_id(message: Message) -> None:
    await message.answer(f"CHANNEL_ID = {config.channel_id or '(не задан)'}")


@router.message(Command("test"))
async def cmd_test(message: Message) -> None:
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2 or not args[1].strip().isdigit():
        await message.answer("Использование: /test 123456789 (nm_id товара)")
        return

    nm_id = int(args[1].strip())
    await message.answer(f"Пробую получить карточку nm={nm_id}…")

    import aiohttp
    from wb.api import fetch_product, fetch_description
    from bot.poster import build_caption

    async with aiohttp.ClientSession() as session:
        product = await fetch_product(session, nm_id)
        if not product:
            await message.answer("Не удалось получить товар 😕")
            return
        description = await fetch_description(session, nm_id)

    log.info(f"Карточка nm={nm_id}: {product}")
    await message.answer(
        "Готово. Данные:\n"
        f"Название: {product['name']}\n"
        f"Цена: {product['price']} ₽ (было {product['old_price']} ₽)\n"
        f"Есть описание: {'да' if description else 'нет'}\n\n"
        "Превью поста:\n"
        f"{build_caption(product, description)}",
        parse_mode="HTML",
  )
