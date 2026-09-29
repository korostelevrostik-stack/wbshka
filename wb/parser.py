import asyncio
import aiohttp

from config import config
from utils.logger import log

SEARCH_API = "https://search.wb.ru/exactmatch/ru/common/v9/search"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

PAGE_SIZE = 100
MAX_PAGES = 10  # предохранитель, чтобы не улететь в бесконечность


async def fetch_category_nm_ids(
    session: aiohttp.ClientSession,
    query: str,
    max_pages: int = MAX_PAGES,
) -> list[int]:
    """
    Возвращает список nm_id по поисковому запросу (категории).
    WB отдаёт ~100 товаров на страницу.
    """
    nm_ids: list[int] = []
    seen: set[int] = set()

    for page in range(1, max_pages + 1):
        params = {
            "appType": 1,
            "curr": "rub",
            "dest": config.wb_dest,
            "query": query,
            "resultset": "catalog",
            "sort": "popular",
            "spp": 30,
            "page": page,
        }

        try:
            async with session.get(
                SEARCH_API, params=params, headers=HEADERS, timeout=20
            ) as resp:
                if resp.status != 200:
                    log.warning(f"Поиск {resp.status} для '{query}' стр.{page}")
                    break
                data = await resp.json()
        except Exception as e:
            log.error(f"Ошибка поиска '{query}' стр.{page}: {e}")
            break

        products = data.get("data", {}).get("products") or []
        if not products:
            break  # товары закончились

        for p in products:
            nm = p.get("id")
            if nm and nm not in seen:
                seen.add(nm)
                nm_ids.append(nm)

        log.info(f"'{query}' стр.{page}: +{len(products)} (всего {len(nm_ids)})")
        await asyncio.sleep(0.5)  # пауза, чтобы не получить бан

    return nm_ids
