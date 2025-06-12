from tortoise import Tortoise
from app.core.config import settings

TORTOISE_ORM = {
    "connections": {
        "default": "postgres://market_user:1234@localhost:5432/market"
    },
    "apps": {
        "models": {
            "models": ["app.models.user", "app.models.order", "app.models.instrument"],
            "default_connection": "default",
        },
    },
}

async def init_db():
    """Initialize database connection"""
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()