from fastapi import FastAPI
from app.services.db import lifespan
from app.api import public

app = FastAPI(lifespan=lifespan)

app.include_router(public.router)