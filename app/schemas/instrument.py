from pydantic import BaseModel, Field
from typing import List
from uuid import UUID

class InstrumentCreate(BaseModel):
    name: str = Field(..., title="Name")
    ticker: str = Field(
        ...,
        title="Ticker",
        pattern=r'^[A-Z]{2,10}$',
        examples=["BTC", "MEMCOIN"],
        min_length=2,
        max_length=10
    )

# class InstrumentResponse(BaseModel):
#     id: UUID
#     ticker: str
#     name: str
#     description: str | None = None
# 
# class InstrumentListResponse(BaseModel):
#     root: List[InstrumentResponse] 