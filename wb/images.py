from wb.api import _basket_number


def image_url(nm_id: int, index: int = 1, size: str = "big") -> str:
    vol = nm_id // 100000
    part = nm_id // 1000
    basket = _basket_number(vol)
    return (
        f"https://basket-{basket}.wbbasket.ru/"
        f"vol{vol}/part{part}/{nm_id}/images/{size}/{index}.webp"
    )
