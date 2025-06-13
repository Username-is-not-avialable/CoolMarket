from tortoise import Tortoise
from app.core.config import settings
from dotenv import load_dotenv
from os import getenv

load_dotenv()
DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_HOST = getenv("DB_HOST")
DB_PORT = getenv("DB_PORT")
DB_NAME = getenv("DB_NAME")

TORTOISE_ORM = {
    "connections": {
        "default": f"postgres://{DB_USER}:1234@localhost:5432/market"
    },
    "apps": {
        "models": {
            "models": ["app.models.user", "app.models.order", "app.models.instrument", "app.models.balance", "aerich.models"],
            "default_connection": "default",
        },
    },
}

async def init_db():
    """Initialize database connection"""
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()