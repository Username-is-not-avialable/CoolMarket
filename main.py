from fastapi import FastAPI
from app.services.db import lifespan
from app.api import public_router, admin_router, order_router

app = FastAPI(lifespan=lifespan)

app.include_router(public_router)
app.include_router(admin_router)
app.include_router(order_router)