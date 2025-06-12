from pydantic import BaseModel, Field, field_validator, UUID4, PositiveInt
from uuid import UUID

class Body_deposit_api_v1_admin_balance_deposit_post(BaseModel):
    user_id: UUID4
    ticker: str
    amount: PositiveInt

    @field_validator('amount')
    def validate_amount(cls, v):
        if v < 1:
            raise ValueError("Количество должно быть большу нуля")
        return v

class BalanceDepositRequest(BaseModel):
    user_id: UUID
    amount: float = Field(..., gt=0)

class BalanceWithdrawRequest(BaseModel):
    user_id: UUID
    amount: float = Field(..., gt=0)

class BalanceResponse(BaseModel):
    user_id: UUID
    amount: float
