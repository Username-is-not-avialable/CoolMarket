from pydantic import BaseModel, Field, field_validator
from typing import Optional

class OrderCreate(BaseModel):
    direction: str = Field(..., description="Direction of the order (BUY or SELL)")
    ticker: str = Field(..., description="Ticker symbol of the instrument")
    qty: int = Field(..., gt=0, description="Quantity of the order")
    price: Optional[int] = Field(None, gt=0, description="Price of the order (optional for market orders)")

    @field_validator('direction')
    def validate_direction(cls, v):
        if v not in ["BUY", "SELL"]:
            raise ValueError("Direction must be either 'BUY' or 'SELL'")
        return v

class OrderResponse(BaseModel):
    success: bool = True
    order_id: str 