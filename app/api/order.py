from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.models.order import Order
from app.models.instrument import Instrument
from app.models.user import User
from app.schemas.order import (
    OrderCreateRequest,
    OrderCreateResponse,
    OrderDetailResponse,
    OrderListResponse,
    OrderDeleteResponse,
    OrderBodyResponse
)

router = APIRouter(prefix="/order", tags=["order"])

@router.post("", response_model=OrderCreateResponse)
async def create_order(order: OrderCreateRequest, authorization: Optional[str] = Header(None)):
    """Create a new order"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is missing")
    
    # Remove 'TOKEN ' prefix if present
    token = authorization.replace('TOKEN ', '') if authorization.startswith('TOKEN ') else authorization
    
    user = await User.get_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check if instrument exists
    instrument = await Instrument.get_by_ticker(order.ticker)
    if not instrument:
        raise HTTPException(status_code=404, detail=f"Instrument {order.ticker} not found")
    
    # Create order
    order_obj = await Order.create(
        user_id=user.id,
        status="NEW",
        body=order.model_dump(),
        filled=0
    )
    
    return OrderCreateResponse(order_id=str(order_obj.id))

@router.get("/order", response_model=OrderListResponse)
async def get_orders(authorization: str = Header(...)):
    """Get all orders for the authenticated user"""
    # Get user from token
    user = await User.get_by_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Get all orders for user
    orders = await Order.find({"user_id": str(user.id)}).to_list()
    
    # Format orders for response
    order_list = []
    for order in orders:
        order_list.append(
            OrderDetailResponse(
                id=str(order.id),
                status=order.status,
                user_id=order.user_id,
                timestamp=order.created_at,
                body=OrderBodyResponse(**order.body),
                filled=order.filled
            )
        )
    
    return OrderListResponse(root=order_list)

@router.get("/order/{order_id}", response_model=OrderDetailResponse)
async def get_order(order_id: UUID, authorization: str = Header(...)):
    """Get information about a specific order"""
    # Get user from token
    user = await User.get_by_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Get order
    order = await Order.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
# Check if order belongs to user
    if order.user_id != str(user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return OrderDetailResponse(
        id=str(order.id),
        status=order.status,
        user_id=order.user_id,
        timestamp=order.created_at,
        body=OrderBodyResponse(**order.body),
        filled=order.filled
    )

@router.delete("/order/{order_id}", response_model=OrderDeleteResponse)
async def delete_order(order_id: UUID, authorization: str = Header(...)):
    """Delete an order"""
    # Get user from token
    user = await User.get_by_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Get order
    order = await Order.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if order belongs to user
    if order.user_id != str(user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if order can be deleted (only NEW orders can be deleted)
    if order.status != "NEW":
        raise HTTPException(status_code=400, detail="Order cannot be deleted")
    
    # Delete order
    await order.delete()
    
    return OrderDeleteResponse()