from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.models.balance import Balance
from app.models.instrument import Instrument
from app.models.user import User
from app.schemas.balance import (Body_deposit_api_v1_admin_balance_deposit_post,
                                 Body_withdraw_api_v1_admin_balance_withdraw_post)
from app.schemas.schemas import Instrument_schema
from app.services.auth import get_user_by_token
from uuid import UUID

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

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

@router.post("/balance/withdraw")
async def withdraw_balance(
    withdraw_data: Body_withdraw_api_v1_admin_balance_withdraw_post,
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

@router.post("/balance/deposit")
async def deposit_balance(
    deposit_data: Body_deposit_api_v1_admin_balance_deposit_post,
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

@router.post("/instrument")
async def add_instrument(
    instrument_data: Instrument_schema,
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """
    Добавление нового инструмента (только для администраторов)
    
    Args:
        instrument_data: Данные инструмента (name и ticker)
        authorization: Токен авторизации в заголовке
        
    Returns:
        dict: {"success": True} при успешном добавлении
        
    Raises:
        HTTPException: 403 - если пользователь не администратор
        HTTPException: 409 - если инструмент с таким тикером уже существует
    """
    # Проверяем токен и получаем пользователя
    admin_user = await get_user_by_token(authorization)
    
    # Проверяем, что пользователь - администратор
    if admin_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only admin users can perform this action"
        )
    
    # Проверяем, не существует ли уже инструмент с таким тикером
    existing_instrument = await Instrument.get_or_none(ticker=instrument_data.ticker)
    if existing_instrument:
        raise HTTPException(
            status_code=409,
            detail="Instrument with this ticker already exists"
        )
    
    # Создаем новый инструмент
    new_instrument = await Instrument.create(
        name=instrument_data.name,
        ticker=instrument_data.ticker,
        is_active=True
    )
    
    return {"success": True}

