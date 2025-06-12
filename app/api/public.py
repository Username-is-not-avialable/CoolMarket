from fastapi import APIRouter, HTTPException, Query
from app.models.user import User
from app.models.instrument import Instrument
from app.models.order import Order
from app.schemas.user import UserCreate, UserResponse
# from app.schemas.instrument import InstrumentListResponse
from app.schemas.orderbook import OrderbookResponse, PriceLevel
from app.schemas.transaction import TransactionResponse
from typing import List
import uuid
from tortoise.expressions import RawSQL

router = APIRouter(prefix="/public", tags=["public"])

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    # Check if user with this name already exists
    if await User.filter(name=user_data.name).exists():
        raise HTTPException(status_code=400, detail="User with this name already exists")
    
    # Create new user
    user = await User.create(
        name=user_data.name,
        api_key=str(uuid.uuid4())  # Generate random API key
    )
    
    return UserResponse(
        id=user.id,
        name=user.name,
        api_key=user.api_key
    )

@router.get("/instrument")
async def instrument():
    instruments = await Instrument.all().values("name", "ticker")
    return instruments

@router.get("/orderbook/{ticker}", response_model=OrderbookResponse)
async def get_orderbook(
    ticker: str,
    limit: int = Query(default=10, ge=1, le=100)
):
    """Get current orderbook for a specific instrument"""
    # Check if instrument exists
    instrument = await Instrument.get_or_none(ticker=ticker)
    if not instrument:
        raise HTTPException(status_code=404, detail=f"Instrument {ticker} not found")
    
    # Get active orders

    orders = await Order.filter(
        status="NEW",
        body__contains={"ticker": ticker}  # Фильтрация по ticker в JSON
    ).all()

    # Сортировка по убыванию цены
    active_orders = sorted(
        orders,
        key=lambda x: x.body.get("price", 0),
        reverse=True
    )
    
    # Separate buy and sell orders
    bid_levels = {}  # price -> total_qty for buy orders
    ask_levels = {}  # price -> total_qty for sell orders
    
    for order in active_orders:
        price = order.body["price"]
        qty = order.body["qty"]
        direction = order.body["direction"]
        
        if direction == "BUY":
            bid_levels[price] = bid_levels.get(price, 0) + qty
        else:  # SELL
            ask_levels[price] = ask_levels.get(price, 0) + qty
    
    # Convert to list of PriceLevel objects and sort
    bid_levels_list = [
        PriceLevel(price=price, qty=qty)
        for price, qty in sorted(bid_levels.items(), reverse=True)[:limit]
    ]
    
    ask_levels_list = [
        PriceLevel(price=price, qty=qty)
        for price, qty in sorted(ask_levels.items())[:limit]
    ]
    
    return OrderbookResponse(
        bid_levels=bid_levels_list,
        ask_levels=ask_levels_list
    )

@router.get("/transactions/{ticker}", response_model=List[TransactionResponse])
async def get_transactions(
    ticker: str,
    limit: int = Query(default=10, ge=1, le=100)
):
    """Get transaction history for a specific instrument"""
    # Check if instrument exists
    instrument = await Instrument.get_or_none(ticker=ticker)
    if not instrument:
        raise HTTPException(status_code=404, detail=f"Instrument {ticker} not found")
    
    # Get filled orders
    filled_orders = await Order.filter(
        status="FILLED",
        body__ticker=ticker
    ).order_by("-created_at").limit(limit)
    
    # Convert to transaction list
    transactions = []
    for order in filled_orders:
        transactions.append(
            TransactionResponse(
                ticker=order.body["ticker"],
                amount=order.body["qty"],
                price=order.body["price"],
                timestamp=order.created_at
            )
        )
    
    return transactions 