from aiogram import Bot
from aiogram.types import URLInputFile
from wb.images import image_url
from utils.logger import log

CAPTION_LIMIT = 1024


def build_caption(product: dict, description: str | None) -> str:
    parts = [f"🛍 <b>{product['name']}</b>"]

    if product.get("brand"):
        parts.append(f"🏷 {product['brand']}")

    price = product["price"]
    old_price = product["old_price"]
    if old_price and old_price > price:
        discount = round((1 - price / old_price) * 100)
        parts.append(f"💰 <b>{price:.0f} ₽</b>  <s>{old_price:.0f} ₽</s>  −{discount}%")
    else:
        parts.append(f"💰 <b>{price:.0f} ₽</b>")

    if product.get("rating"):
        parts.append(f"⭐ {product['rating']} ({product.get('feedbacks', 0)})")

    parts.append(
        f"🔗 <a href='https://wildberries.ru/catalog/{product['nm_id']}/detail.aspx'>"
        f"Открыть на WB</a>"
    )

    caption = "\n".join(parts)

    if description:
        # оставляем место под описание с учётом caption-лимита
        head = caption
        tail = f"\n\n📝 {description}"
        if len(head) + len(tail) <= CAPTION_LIMIT:
            return head + tail
        # обрезаем описание
        available = CAPTION_LIMIT - len(head) - len("\n\n📝 …")
        if available > 60:
            return head + "\n\n📝 " + description[:available].rstrip() + "…"
    return caption


async def post_product(bot: Bot, product: dict, description: str | None) -> bool:
    caption = build_caption(product, description)
    photo = URLInputFile(image_url(product["nm_id"]))

    try:
        await bot.send_photo(
            chat_id=_channel_id(),
            photo=photo,
            caption=caption,
            parse_mode="HTML",
        )
        return True
    except Exception as e:
        log.error(f"Не удалось запостить nm={product['nm_id']}: {e}")
        return False


def _channel_id() -> str:
    from config import config
    return config.channel_id
