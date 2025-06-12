from fastapi import APIRouter, Header, HTTPException, Depends
from typing import Optional
from app.models.user import User
from app.models.balance import Balance
from app.schemas.balance import BalanceDepositRequest, BalanceWithdrawRequest
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
@router.post("/balance/deposit")
async def deposit_balance(
    deposit_data: BalanceDepositRequest,
    authorization: str = Header(None, alias="Authorization"),
):
    """
    Пополнение баланса пользователя (только для администраторов)
    
    Требуемые параметры:
    - user_id: UUID пользователя
    - ticker: Тикер инструмента (например, "MEMCOIN")
    - amount: Сумма пополнения (целое число > 0)
    """
    # Проверяем авторизацию и права администратора
    admin_user = await get_user_by_token(authorization)
    if admin_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only admin users can perform this action"
        )

    # Проверяем существование пользователя
    user = await User.get_or_none(id=deposit_data.user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Проверяем существование инструмента
    instrument = await Instrument.get_or_none(ticker=deposit_data.ticker)
    if not instrument:
        raise HTTPException(
            status_code=404,
            detail="Instrument not found"
        )

    # Проверяем сумму (должна быть положительной)
    if deposit_data.amount <= 0:
        raise HTTPException(
            status_code=422,
            detail="Amount must be positive"
        )

    # Обновляем баланс (или создаем новую запись)
    balance, created = await Balance.get_or_create(
        user=user,
        instrument=instrument,
        defaults={"amount": deposit_data.amount}
    )
    
    if not created:
        balance.amount += deposit_data.amount
        await balance.save()

    return {"success": True}

@router.post("/balance/withdraw")
async def withdraw_balance(
    withdraw_data: BalanceWithdrawRequest,
    authorization: str = Header(None, alias="Authorization"),
):
    """
    Списание средств с баланса пользователя (только для администраторов)
    
    Требуемые параметры:
    - user_id: UUID пользователя
    - ticker: Тикер инструмента (например, "MEMCOIN")
    - amount: Сумма списания (целое число > 0)
    """
    # Проверяем авторизацию и права администратора
    admin_user = await get_user_by_token(authorization)
    if admin_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only admin users can perform this action"
        )

    # Проверяем существование пользователя
    user = await User.get_or_none(id=withdraw_data.user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Проверяем существование инструмента
    instrument = await Instrument.get_or_none(ticker=withdraw_data.ticker)
    if not instrument:
        raise HTTPException(
            status_code=404,
            detail="Instrument not found"
        )

    # Проверяем сумму (должна быть положительной)
    if withdraw_data.amount <= 0:
        raise HTTPException(
            status_code=422,
            detail="Amount must be positive"
        )

    # Проверка существования баланса пользователя
    balance = await Balance.get_or_none(
        user=user,
        instrument=instrument
    )
    
    # Если баланса нет или средств недостаточно
    if not balance or balance.amount < withdraw_data.amount:
        current_balance = balance.amount if balance else 0
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Insufficient funds",
                "current_balance": current_balance,
                "required": withdraw_data.amount
            }
        )

    # Списание средств
    balance.amount -= withdraw_data.amount
    await balance.save()

    return {"success": True}