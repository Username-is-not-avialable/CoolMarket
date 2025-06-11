from fastapi import APIRouter, Header, HTTPException
from app.services.auth import get_user_by_token
from app.models.balance import Balance

router = APIRouter(prefix="/api/v1/balance", tags=["Balance"])

@router.get("/")
async def get_balances(
    authorization: str = Header(..., alias="Authorization")
):
    user = await get_user_by_token(authorization)
    balances = await Balance.filter(user=user).prefetch_related("instrument")
    return {bal.instrument.ticker: bal.amount for bal in balances}