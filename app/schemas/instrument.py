from pydantic import BaseModel, Field
from typing import List
from uuid import UUID

class InstrumentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the instrument")
    ticker: str = Field(..., min_length=1, max_length=10, description="Ticker symbol of the instrument")

class InstrumentResponse(BaseModel):
    id: UUID
    ticker: str
    name: str
    description: str | None = None

class InstrumentListResponse(BaseModel):
    root: List[InstrumentResponse] 