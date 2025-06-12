from tortoise import Tortoise
from app.core.config import settings
from dotenv import load_dotenv
from os import getenv

user = getenv("DB_USER")
password = getenv("DB_PASSWORD")
TORTOISE_ORM = {
    "connections": {
        "default": f"postgres://{user}:{password}@localhost:5432/market"
    },
    "apps": {
        "models": {
            "models": ["app.models.user", "app.models.order", "app.models.instrument", "app.models.balance"],
            "default_connection": "default",
        },
    },
}

async def init_db():
    """Initialize database connection"""
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()