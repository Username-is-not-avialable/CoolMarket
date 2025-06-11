from contextlib import asynccontextmanager
from tortoise import Tortoise
from dotenv import load_dotenv
from os import getenv

load_dotenv()

user = getenv("DB_USER")
password = getenv("DB_PASSWORD")
async def init_db():
    await Tortoise.init(
        db_url=f"postgres://{user}:{password}@localhost:5432/market",
        modules={
            "models": [
                "app.models.user",
                "app.models.order",
                "app.models.instrument",
                "app.models.balance"
            ]
        }
    )
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()

@asynccontextmanager
async def lifespan(app: 'FastAPI'):
    await init_db()
    yield
    await close_db()

