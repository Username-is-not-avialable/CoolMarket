from fastapi import APIRouter, Header, HTTPException
from app.services.auth import get_user_by_token
from app.models.order import Order
from app.models.instrument import Instrument
from app.schemas.order import (
    OrderCreate, OrderResponse, OrderListResponse, 
    OrderListItem, OrderBody, OrderDetailResponse,
    OrderDeleteResponse
)
import uuid
from datetime import datetime

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

@router.get("/order", response_model=OrderListResponse)
async def get_orders(
    authorization: str = Header(..., alias="Authorization")
):
    # Получаем пользователя по токену
    user = await get_user_by_token(authorization)
    
    # Получаем все ордера пользователя
    orders = await Order.filter(user=user).prefetch_related('instrument')
    
    # Преобразуем ордера в нужный формат
    order_list = []
    for order in orders:
        order_list.append(
            OrderListItem(
                id=str(order.id),
                status=order.status,
                user_id=str(user.id),
                timestamp=order.created_at,
                body=OrderBody(
                    direction=order.direction,
                    ticker=order.instrument.ticker,
                    qty=order.quantity,
                    price=order.price
                ),
                filled=0  # TODO: Добавить логику подсчета исполненных ордеров
            )
        )
    
    return OrderListResponse(__root__=order_list)

@router.get("/order/{order_id}", response_model=OrderDetailResponse)
async def get_order(
    order_id: uuid.UUID,
    authorization: str = Header(..., alias="Authorization")
):
    # Получаем пользователя по токену
    user = await get_user_by_token(authorization)
    
    # Получаем ордер
    order = await Order.get_or_none(id=order_id).prefetch_related('instrument')
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )
    
    # Проверяем, что ордер принадлежит пользователю
    if order.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    
    return OrderDetailResponse(
        id=str(order.id),
        status=order.status,
        user_id=str(user.id),
        timestamp=order.created_at,
        body=OrderBody(
            direction=order.direction,
            ticker=order.instrument.ticker,
            qty=order.quantity,
            price=order.price
        ),
        filled=0  # TODO: Добавить логику подсчета исполненных ордеров
    )

@router.delete("/order/{order_id}", response_model=OrderDeleteResponse)
async def delete_order(
    order_id: uuid.UUID,
    authorization: str = Header(..., alias="Authorization")
):
    # Получаем пользователя по токену
    user = await get_user_by_token(authorization)
    
    # Получаем ордер
    order = await Order.get_or_none(id=order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )
    
    # Проверяем, что ордер принадлежит пользователю
    if order.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    
    # Проверяем, что ордер можно удалить (только NEW)
    if order.status != "NEW":
        raise HTTPException(
            status_code=400,
            detail="Can only delete orders with NEW status"
        )
    
    # Удаляем ордер
    await order.delete()
    
    return OrderDeleteResponse(success=True) 