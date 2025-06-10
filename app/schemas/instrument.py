from pydantic import BaseModel, Field

class InstrumentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the instrument")
    ticker: str = Field(..., min_length=1, max_length=10, description="Ticker symbol of the instrument")

class InstrumentResponse(BaseModel):
    success: bool = True 