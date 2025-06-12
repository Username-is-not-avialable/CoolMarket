from pydantic import BaseModel
from datetime import datetime

class TransactionResponse(BaseModel):
    ticker: str
    amount: int
    price: float
    timestamp: datetime 