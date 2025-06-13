from pydantic import BaseModel, Field, ValidationError, field_validator, RootModel, model_validator
from typing import Literal, Optional, List, Union
from datetime import datetime
from uuid import UUID
from enum import Enum

class OrderDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"

class OrderStatus(str, Enum):
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class Direction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class LimitOrderBody(BaseModel):
    """Схема для лимитного ордера"""
    direction: Direction = Field(
        ...,
        description="Direction of the order (BUY or SELL)",
        examples=["BUY", "SELL"]
    )
    ticker: str = Field(
        ...,
        description="Ticker symbol of the instrument",
        examples=["BTC", "ETH"],
        min_length=2,
        max_length=10
    )
    qty: int = Field(
        ...,
        gt=0,
        description="Quantity of the order",
        examples=[1, 10, 100]
    )
    price: int = Field(
        ...,
        gt=0,
        description="Price of the order",
        examples=[50000, 3000]
    )

class MarketOrderBody(BaseModel):
    """Схема для рыночного ордера"""
    direction: Direction = Field(
        ...,
        description="Direction of the order (BUY or SELL)",
        examples=["BUY", "SELL"]
    )
    ticker: str = Field(
        ...,
        description="Ticker symbol of the instrument",
        examples=["BTC", "ETH"],
        min_length=2,
        max_length=10
    )
    qty: int = Field(
        ...,
        gt=0,
        description="Quantity of the order",
        examples=[1, 10, 100]
    )

class OrderCreateRequest(BaseModel):
    # Заменяем Union на ручную валидацию
    direction: Direction
    ticker: str
    qty: int
    price: Optional[int] = None  # Для рыночных ордеров

    @model_validator(mode='after')
    def validate_order(self):
        if self.price is not None:
            # Валидируем как LimitOrderBody
            return LimitOrderBody.model_validate(self.model_dump())
        return MarketOrderBody.model_validate(self.model_dump())

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
