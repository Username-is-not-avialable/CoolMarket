from pydantic import BaseModel, Field, field_validator

class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=20, 
                     examples=["Alice"], 
                     description="Никнейм (3-20 символов)")

    @field_validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Никнейм слишком короткий")
        return v

class UserResponse(BaseModel):
    id: int
    name: str
    api_key: str

# Другие схемы (для ордеров, инструментов и т.д.)
class InstrumentCreate(BaseModel):
    ticker: str
    name: str