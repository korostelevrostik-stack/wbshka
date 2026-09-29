import asyncio
import aiohttp
from aiogram import Bot

from config import config
from db.repository import repo
from wb.api import fetch_product, fetch_description
from wb.parser import fetch_category_nm_ids
from bot.poster import post_product
from utils.logger import log

# Список поисковых запросов = "категорий"
CATEGORIES = [
    "чехол iphone 15",
    "беспроводные наушники",
    "умные часы",
    # добавляйте свои
]

POSTS_PER_RUN = 20        # максимум постов за один прогон
DELAY_BETWEEN_POSTS = 3   # секунд между постами в канал


async def scan_once(bot: Bot) -> None:
    """Один прогон: собрать товары, отфильтровать, запостить новые."""
    log.info("🔍 Старт сканирования")
    posted_count = 0

    async with aiohttp.ClientSession() as session:
        for query in CATEGORIES:
            if posted_count >= POSTS_PER_RUN:
                break

            nm_ids = await fetch_category_nm_ids(session, query)
            log.info(f"'{query}': найдено {len(nm_ids)} артикулов")

            for nm_id in nm_ids:
                if posted_count >= POSTS_PER_RUN:
                    break

                # 1. Проверка на дубли
                if repo.is_posted(nm_id):
                    continue

                # 2. Получаем карточку
                product = await fetch_product(session, nm_id)
                if not product:
                    continue

                # 3. Фильтр по минимальной цене
                if product["price"] < config.min_price:
                    log.debug(
                        f"nm={nm_id} пропущен: {product['price']} < {config.min_price}"
                    )
                    # помечаем, чтобы не проверять заново
                    repo.mark_posted(nm_id, product["name"], product["price"])
                    continue

                # 4. Описание (может не быть)
                description = await fetch_description(session, nm_id)

                # 5. Постим
                ok = await post_product(bot, product, description)
                if ok:
                    repo.mark_posted(nm_id, product["name"], product["price"])
                    posted_count += 1
                    log.info(
                        f"✅ Запостили nm={nm_id} «{product['name']}» "
                        f"{product['price']}₽"
                    )
                    await asyncio.sleep(DELAY_BETWEEN_POSTS)
                else:
                    await asyncio.sleep(1)

    log.info(f"🏁 Сканирование завершено. Опубликовано: {posted_count}")
