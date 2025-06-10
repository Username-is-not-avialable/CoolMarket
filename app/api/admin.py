from fastapi import APIRouter, Header, HTTPException, Depends
from typing import Optional
from app.models.user import User
from app.services.auth import get_user_by_token
from uuid import UUID
from app.models.instrument import Instrument
from app.schemas.instrument import InstrumentCreate, InstrumentResponse

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

async def verify_admin(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is required")
    
    user = await User.get_or_none(api_key=authorization)
    if not user or user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
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

@router.delete("/user/")
async def delete_user(
    user_id: str,
    authorization: str = Header(..., alias="Authorization"),
):
    print("passed")

@router.post("/instrument", response_model=InstrumentResponse)
async def create_instrument(
    instrument_data: InstrumentCreate,
    _: User = Depends(verify_admin)
):
    # Check if instrument with this ticker already exists
    existing = await Instrument.get_or_none(ticker=instrument_data.ticker)
    if existing:
        raise HTTPException(status_code=400, detail="Instrument with this ticker already exists")
    
    # Create new instrument
    await Instrument.create(
        ticker=instrument_data.ticker,
        name=instrument_data.name
    )
    
    return InstrumentResponse(success=True)