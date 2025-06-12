from pydantic import BaseModel
from typing import List

class PriceLevel(BaseModel):
    price: float
    qty: int

class OrderbookResponse(BaseModel):
    bid_levels: List[PriceLevel]
    ask_levels: List[PriceLevel] 