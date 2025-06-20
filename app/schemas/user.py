from pydantic import BaseModel, Field, field_validator, UUID4

class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=20, 
                     examples=["Alice"], 
                     description="Никнейм (3-20 символов)")

    @field_validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Никнейм слишком короткий")
        return v

class InstrumentCreate(BaseModel):
    ticker: str
    name: str

class UserResponse(BaseModel):
    id: UUID4
    name: str
    api_key: str