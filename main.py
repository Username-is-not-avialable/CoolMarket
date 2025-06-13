from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, instrument, order, public, admin, balance
from app.core.config import settings
from app.core.database import init_db
from app.services.logging import log_requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Логи в файл
        logging.StreamHandler()         # Логи в консоль
    ]
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
app.middleware("http")(log_requests)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth, prefix=settings.API_V1_STR)
app.include_router(instrument, prefix=settings.API_V1_STR)
app.include_router(order, prefix=settings.API_V1_STR)
app.include_router(public, prefix=settings.API_V1_STR)
app.include_router(admin, prefix=settings.API_V1_STR)
app.include_router(balance, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    await init_db()