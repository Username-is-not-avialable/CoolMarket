from pydantic import BaseModel, Field, field_validator, UUID4, PositiveInt
from uuid import UUID

class BalanceDepositRequest(BaseModel):
    user_id: UUID4
    ticker: str
    amount: PositiveInt

    @field_validator('amount')
    def validate_amount(cls, v):
        if v < 1:
            raise ValueError("Количество должно быть большу нуля")
        return v

class BalanceDepositRequest(BaseModel):
    user_id: UUID4
    ticker: str
    amount: PositiveInt

    @field_validator('amount')
    def validate_amount(cls, v):
        if v < 1:
            raise ValueError("Количество должно быть большу нуля")
        return v

class BalanceWithdrawRequest(BaseModel):
    user_id: UUID4
    ticker: str
    amount: PositiveInt

    @field_validator('amount')
    def validate_amount(cls, v):
        if v < 1:
            raise ValueError("Количество должно быть большу нуля")
        return v
