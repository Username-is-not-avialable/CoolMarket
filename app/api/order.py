from fastapi import APIRouter, HTTPException, Header, Depends, Security
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from fastapi.security import APIKeyHeader

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

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def get_current_user(authorization: str = Security(api_key_header)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is missing")
    
    # Remove 'TOKEN ' prefix if present
    token = authorization.replace('TOKEN ', '') if authorization.startswith('TOKEN ') else authorization
    
    user = await User.get_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user

@router.post("", response_model=OrderCreateResponse)
async def create_order(
    order: OrderCreateRequest,
    user: User = Depends(get_current_user)
):
    """Create a new order"""
    # Check if instrument exists
    instrument = await Instrument.get_by_ticker(order.ticker)
    if not instrument:
        raise HTTPException(status_code=404, detail=f"Instrument {order.ticker} not found")
    
    # Create order with explicit UUID conversion
    order_obj = await Order.create(
        user_id=user.id,  # user.id is already UUID
        status="NEW",
        body=order.model_dump(),
        filled=0
    )
    
    return OrderCreateResponse(order_id=str(order_obj.id))

@router.get("", response_model=List[OrderDetailResponse])
async def get_orders(user: User = Depends(get_current_user)):
    """Get all orders for the authenticated user"""
    # Get all orders for user
    orders = await Order.filter(user_id=str(user.id))
    
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
    
    return order_list

@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order(
    order_id: UUID,
    user: User = Depends(get_current_user)
):
    """Get information about a specific order"""
    # Get order
    order = await Order.get_or_none(id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Debug information
    print(f"Order user_id: {order.user_id}, type: {type(order.user_id)}")
    print(f"User id: {user.id}, type: {type(user.id)}")
    
    # Check if order belongs to user
    if str(order.user_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return OrderDetailResponse(
        id=str(order.id),
        status=order.status,
        user_id=order.user_id,
        timestamp=order.created_at,
        body=OrderBodyResponse(**order.body),
        filled=order.filled
    )

@router.delete("/{order_id}", response_model=OrderDeleteResponse)
async def delete_order(
    order_id: UUID,
    user: User = Depends(get_current_user)
):
    """Delete an order"""
    # Get order
    order = await Order.get_or_none(id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Debug information
    print(f"Order user_id: {order.user_id}, type: {type(order.user_id)}")
    print(f"User id: {user.id}, type: {type(user.id)}")
    
    # Check if order belongs to user
    if str(order.user_id) != str(user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if order can be deleted (only NEW orders can be deleted)
    if order.status != "NEW":
        raise HTTPException(status_code=400, detail="Order cannot be deleted")
    
    # Delete order
    await order.delete()
    
    return OrderDeleteResponse()