from fastapi import FastAPI
from app.services.db import lifespan
from app.api import public, admin, user, balance

app = FastAPI(lifespan=lifespan)

app.include_router(public.router)
app.include_router(admin.router)
# app.include_router(user.router)
app.include_router(balance.router)