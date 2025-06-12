from fastapi import APIRouter, Header, HTTPException, Depends
from typing import Optional
from app.models.user import User
from app.models.balance import Balance
from app.schemas.balance import Body_deposit_api_v1_admin_balance_deposit_post, BalanceDepositRequest, BalanceWithdrawRequest, BalanceResponse
from app.services.auth import get_user_by_token
from uuid import UUID
from app.models.instrument import Instrument
from app.schemas.instrument import InstrumentCreate

router = APIRouter(prefix="/admin",tags=["admin"])

async def verify_admin(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is missing")
    
    # Remove 'TOKEN ' prefix if present
    token = authorization.replace('TOKEN ', '') if authorization.startswith('TOKEN ') else authorization
    
    user = await User.get_by_token(token)
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    return user

@router.delete("/user/{user_id}")
async def delete_user(
    user_id: str,
    authorization: str = Header(..., alias="Authorization"),
):
    # Проверяем токен и получаем пользователя
    admin_user = await get_user_by_token(authorization)

    # Проверяем, что пользователь - администратор
    if admin_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only admin users can perform this action"
        )
    
    # Удаляем целевого пользователя
    deleted_count = await User.filter(id=user_id).delete()
    
    if not deleted_count:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return {"success": True}

@router.post("/instrument")
async def create_instrument(
    instrument: InstrumentCreate,
    authorization: str = Header(..., alias="Authorization")
):
    admin_user = await get_user_by_token(authorization)
    print(admin_user.role)
    if admin_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    # Проверяем, что тикер уникален
    exists = await Instrument.get_or_none(ticker=instrument.ticker)
    if exists:
        raise HTTPException(status_code=400, detail="Instrument with this ticker already exists")
    await Instrument.create(name=instrument.name, ticker=instrument.ticker)
    return {"success": True}
@router.post("/balance/deposit", response_model=BalanceResponse)
async def deposit_balance(
    request: BalanceDepositRequest,
    admin: User = Depends(verify_admin)
):
    """Deposit funds to user's balance"""
    user = await User.get_or_none(id=request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    balance = await Balance.get_or_create(user_id=request.user_id)
    balance.amount += request.amount
    await balance.save()
    
    return BalanceResponse(
        user_id=balance.user_id,
        amount=balance.amount
    )

@router.post("/balance/withdraw", response_model=BalanceResponse)
async def withdraw_balance(
    request: BalanceWithdrawRequest,
    admin: User = Depends(verify_admin)
):
    """Withdraw funds from user's balance"""
    user = await User.get_or_none(id=request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    balance = await Balance.get_or_none(user_id=request.user_id)
    if not balance:
        raise HTTPException(status_code=404, detail="Balance not found")
    
    if balance.amount < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    balance.amount -= request.amount
    await balance.save()
    
    return BalanceResponse(
        user_id=balance.user_id,
        amount=balance.amount
    )
