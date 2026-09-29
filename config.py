import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    bot_token: str
    channel_id: str
    wb_dest: int
    min_price: float
    scan_interval: int
    db_path: str
    log_level: str
    proxy_url: str | None
    categories: list[str] = field(default_factory=list)


def load_config() -> Config:
    return Config(
        bot_token=os.getenv("BOT_TOKEN", ""),
        channel_id=os.getenv("CHANNEL_ID", ""),
        wb_dest=int(os.getenv("WB_DEST", "-1257786")),
        min_price=float(os.getenv("MIN_PRICE", "1000")),
        scan_interval=int(os.getenv("SCAN_INTERVAL", "30")),
        db_path=os.getenv("DB_PATH", "data/wb_bot.db"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        proxy_url=os.getenv("PROXY_URL") or None,
        categories=[
            c.strip()
            for c in os.getenv("CATEGORIES", "").split(",")
            if c.strip()
        ],
    )


config = load_config()
