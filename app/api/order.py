from fastapi import APIRouter, Header, HTTPException
from app.services.auth import get_user_by_token
from app.models.order import Order
from app.models.instrument import Instrument
from app.schemas.order import OrderCreate, OrderResponse
import uuid

router = APIRouter(prefix="/api/v1", tags=["Order"])

@router.post("/order", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    authorization: str = Header(..., alias="Authorization")
):
    # Получаем пользователя по токену
    user = await get_user_by_token(authorization)
    
    # Проверяем существование инструмента
    instrument = await Instrument.get_or_none(ticker=order_data.ticker)
    if not instrument:
        raise HTTPException(
            status_code=404,
            detail=f"Instrument with ticker {order_data.ticker} not found"
        )
    
    # Проверяем, что инструмент активен
    if not instrument.is_active:
        raise HTTPException(
            status_code=400,
            detail=f"Instrument {order_data.ticker} is not active"
        )
    
    # Создаем ордер
    order = await Order.create(
        id=uuid.uuid4(),
        user=user,
        instrument=instrument,
        direction=order_data.direction,
        price=order_data.price,
        quantity=order_data.qty,
        status="NEW"
    )
    
    return OrderResponse(
        success=True,
        order_id=str(order.id)
    ) 