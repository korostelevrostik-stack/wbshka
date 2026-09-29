import aiohttp
from config import config
from utils.logger import log

CARD_API = "https://card.wb.ru/cards/v4/detail"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    )
}


async def fetch_product(session: aiohttp.ClientSession, nm_id: int) -> dict | None:
    """Возвращает нормализованную карточку товара или None."""
    params = {
        "appType": 1,
        "curr": "rub",
        "dest": config.wb_dest,
        "spp": 30,
        "nm": nm_id,
    }

    try:
        async with session.get(
            CARD_API, params=params, headers=HEADERS, timeout=15
        ) as resp:
            if resp.status != 200:
                log.warning(f"WB API {resp.status} для nm={nm_id}")
                return None
            data = await resp.json()
    except Exception as e:
        log.error(f"Ошибка запроса к WB для nm={nm_id}: {e}")
        return None

    products = data.get("data", {}).get("products") or []
    if not products:
        return None

    p = products[0]
    price, old_price = _extract_prices(p)

    return {
        "nm_id": p.get("id"),
        "name": p.get("name", ""),
        "brand": p.get("brand", ""),
        "rating": p.get("reviewRating") or p.get("rating") or 0,
        "feedbacks": p.get("feedbacks", 0),
        "price": price,
        "old_price": old_price,
        "quantity": p.get("totalQuantity", 0),
    }


def _extract_prices(product: dict) -> tuple[float, float]:
    """Возвращает (цена со скидкой, старая цена) в рублях."""
    for size in product.get("sizes", []):
        price_obj = size.get("price")
        if not price_obj:
            continue
        product_price = price_obj.get("product") or price_obj.get("total")
        basic_price = price_obj.get("basic") or product_price
        if product_price:
            return product_price / 100, (basic_price or product_price) / 100
    # fallback на старые поля
    sale = product.get("salePriceU")
    basic = product.get("priceU")
    if sale:
        return sale / 100, (basic or sale) / 100
    return 0.0, 0.0


async def fetch_description(
    session: aiohttp.ClientSession, nm_id: int
) -> str | None:
    """Пытается достать описание из card.json на CDN WB."""
    url = _card_json_url(nm_id)
    try:
        async with session.get(url, headers=HEADERS, timeout=10) as resp:
            if resp.status != 200:
                return None
            data = await resp.json(content_type=None)
            return (data.get("description") or "").strip() or None
    except Exception:
        return None


def _card_json_url(nm_id: int) -> str:
    vol = nm_id // 100000
    part = nm_id // 1000
    basket = _basket_number(vol)
    return (
        f"https://basket-{basket}.wbbasket.ru/"
        f"vol{vol}/part{part}/{nm_id}/info/ru/card.json"
    )


def _basket_number(vol: int) -> str:
    ranges = [
        (143, "01"), (287, "02"), (431, "03"), (719, "04"),
        (1007, "05"), (1061, "06"), (1115, "07"), (1169, "08"),
        (1313, "09"), (1601, "10"), (1655, "11"), (1919, "12"),
        (2045, "13"), (2189, "14"), (2405, "15"), (2621, "16"),
        (2837, "17"),
    ]
    for max_vol, num in ranges:
        if vol <= max_vol:
            return num
    return "18"
