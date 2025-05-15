from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    # Добавьте другие поля при необходимости

class UserResponse(BaseModel):
    id: int
    name: str
    api_key: str

# Другие схемы (для ордеров, инструментов и т.д.)
class InstrumentCreate(BaseModel):
    ticker: str
    name: str