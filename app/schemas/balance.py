from pydantic import BaseModel, Field, field_validator, UUID4, PositiveInt

class Body_deposit_api_v1_admin_balance_deposit_post(BaseModel):
    user_id: UUID4
    ticker: str
    amount: PositiveInt

    @field_validator('amount')
    def validate_amount(cls, v):
        if v < 1:
            raise ValueError("Количество должно быть большу нуля")
        return v


class Body_withdraw_api_v1_admin_balance_withdraw_post(BaseModel):
    user_id: UUID4
    ticker: str
    amount: PositiveInt

    @field_validator('amount')
    def validate_amount(cls, v):
        if v < 1:
            raise ValueError("Количество должно быть большу нуля")
        return v