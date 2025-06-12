from pydantic import BaseModel, Field, field_validator, RootModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# Request schemas
class OrderCreateRequest(BaseModel):
    """Схема для создания нового ордера"""
    direction: str = Field(
        ...,
        description="Direction of the order (BUY or SELL)",
        examples=["BUY", "SELL"]
    )
    ticker: str = Field(
        ...,
        description="Ticker symbol of the instrument",
        examples=["BTC", "ETH"]
    )
    qty: int = Field(
        ...,
        gt=0,
        description="Quantity of the order",
        examples=[1, 10, 100]
    )
    price: Optional[float] = Field(
        None,
        gt=0,
        description="Price of the order (optional for market orders)",
        examples=[50000, 3000]
    )

    @field_validator('direction')
    def validate_direction(cls, v):
        if v not in ["BUY", "SELL"]:
            raise ValueError("Direction must be either 'BUY' or 'SELL'")
        return v

# Response schemas
class OrderBodyResponse(BaseModel):
    """Схема для тела ордера в ответе"""
    direction: str
    ticker: str
    qty: int
    price: Optional[float] = None

class OrderDetailResponse(BaseModel):
    """Схема для детальной информации об ордере"""
    id: str
    status: str
    user_id: UUID
    timestamp: datetime
    body: OrderBodyResponse
    filled: int = 0

class OrderListResponse(RootModel):
    """Схема для списка ордеров"""
    root: List[OrderDetailResponse]

class OrderCreateResponse(BaseModel):
    """Схема для ответа при создании ордера"""
    success: bool = True
    order_id: str

class OrderDeleteResponse(BaseModel):
    """Схема для ответа при удалении ордера"""
    success: bool = True 