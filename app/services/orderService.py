import asyncio
from uuid import UUID
from typing import Optional

from tortoise.transactions import in_transaction
from tortoise.expressions import F
from tortoise.exceptions import DoesNotExist, IntegrityError

from fastapi import HTTPException

from app.models.order import (
    Order)
from app.models.balance import (
    Balance)
from app.models.instrument import (
    Instrument)

from app.models.transaction import Transaction
from app.models.user import User

from app.schemas.order import (
    OrderCreateRequest,
    OrderDirection,
    OrderType,
    OrderStatus
)


class OrderService:
    @staticmethod
    async def create_order(order_data: dict):
        """
        Создает и обрабатывает новый ордер
        
        Args:
            order_data: {
                "direction": "BUY/SELL",
                "ticker": str,
                "qty": int,
                "price": Optional[int],
                "user_id": UUID,
                "status": OrderStatus,
                "filled": int,
                "is_market": bool,
                "order_type": "LIMIT/MARKET"
            }
        """
        async with in_transaction():
            # 1. Получаем инструменты
            instrument = await Instrument.get_or_none(ticker=order_data['ticker'])
            rub_instrument = await Instrument.get_or_none(ticker="RUB")  # Для блокировки RUB
            
            if not instrument or not rub_instrument:
                raise ValueError("Instrument not found")

            # 2. Для лимитных ордеров - блокировка средств
            if order_data['order_type'] == OrderType.LIMIT:
                await Balance.filter(
                    user_id=order_data['user_id'],
                    instrument_id=rub_instrument.id  # Фильтруем по ID вместо __ticker
                ).update(
                    locked=F('locked') + (order_data['price'] * order_data['qty'])
                )

            # 3. Создаем ордер
            order = await Order.create(
                user_id=order_data['user_id'],
                status=OrderStatus.NEW,
                direction=order_data['direction'],
                ticker=order_data['ticker'],
                qty=order_data['qty'],
                price=order_data.get('price'),
                filled=0,
                is_market=order_data['order_type'] == OrderType.MARKET
            )

            # Немедленное исполнение для рыночных ордеров
            if order_data['is_market']:
                await OrderService.match_market_order(order)
            
            return order

    @staticmethod
    async def match_market_order(order: Order):
        """
        Исполнение рыночного ордера по лучшей доступной цене
        """
        async with in_transaction():
            # Определяем критерии поиска противоположных ордеров
            opposite_direction = OrderDirection.SELL if order.direction == OrderDirection.BUY else OrderDirection.BUY
            price_order = "price" if order.direction == OrderDirection.BUY else "-price"

            # Ищем подходящие лимитные ордера
            matching_orders = await Order.filter(
                ticker=order.ticker,
                direction=opposite_direction,
                status="NEW",
                order_type=OrderType.LIMIT
            ).order_by(price_order).select_for_update()

            total_executed = 0
            remaining_qty = order.quantity

            for matching_order in matching_orders:
                if remaining_qty <= 0:
                    break

                # Определяем цену исполнения (для покупателя - минимальная из доступных)
                execution_price = matching_order.price

                # Максимально возможный объем для исполнения
                available_qty = matching_order.quantity - matching_order.filled
                execute_qty = min(remaining_qty, available_qty)

                # Создаем запись о сделке
                await Transaction.create(
                    buyer_id=order.user_id if order.direction == OrderDirection.BUY else matching_order.user_id,
                    seller_id=matching_order.user_id if order.direction == OrderDirection.BUY else order.user_id,
                    instrument=await Instrument.get(ticker=order.ticker),
                    price=execution_price,
                    quantity=execute_qty,
                    order_buy=order if order.direction == OrderDirection.BUY else matching_order,
                    order_sell=matching_order if order.direction == OrderDirection.BUY else order
                )

                # Обновляем балансы
                await OrderService.update_balances(
                    order, 
                    matching_order,
                    execute_qty,
                    execution_price
                )

                # Обновляем статусы ордеров
                total_executed += execute_qty
                remaining_qty -= execute_qty

                # Обновляем matching_order
                new_filled = matching_order.filled + execute_qty
                await Order.filter(id=matching_order.id).update(
                    filled=new_filled,
                    status="FILLED" if new_filled >= matching_order.quantity else "PARTIALLY_FILLED"
                )

            # Обновляем статус рыночного ордера
            if total_executed > 0:
                new_filled = order.filled + total_executed
                await Order.filter(id=order.id).update(
                    filled=new_filled,
                    status="FILLED" if new_filled >= order.quantity else "PARTIALLY_FILLED"
                )
            else:
                # Если не нашли подходящих ордеров - сразу отменяем
                await Order.filter(id=order.id).update(
                    status="REJECTED",
                    body=order.body.update({"reason": "No matching orders available"})
                )

    
    @staticmethod
    async def match_limit_order(order: Order):
        opposite_direction = OrderDirection.SELL if order.direction == OrderDirection.BUY else OrderDirection.BUY
        
        async with in_transaction():
            # Находим подходящие противоположные ордера
            matching_orders = await Order.filter(
                ticker=order.ticker,
                direction=opposite_direction,
                status="NEW"
            ).order_by(
                "price" if order.direction == OrderDirection.BUY else "-price"
            ).select_for_update()

            for matching_order in matching_orders:
                if await OrderService.try_match(order, matching_order):
                    break

    @staticmethod
    async def try_match(order1: Order, order2: Order) -> bool:
        # Проверяем возможность исполнения
        if (order1.direction == OrderDirection.BUY and order1.price >= order2.price) or \
           (order1.direction == OrderDirection.SELL and order1.price <= order2.price):
            
            # Создаем транзакцию
            await Transaction.create(
                buyer_id=order1.user_id if order1.direction == OrderDirection.BUY else order2.user_id,
                seller_id=order2.user_id if order1.direction == OrderDirection.BUY else order1.user_id,
                instrument_id=order1.instrument_id,
                price=min(order1.price, order2.price),
                quantity=min(order1.quantity - order1.filled, order2.quantity - order2.filled),
                order_buy=order1 if order1.direction == OrderDirection.BUY else order2,
                order_sell=order2 if order1.direction == OrderDirection.BUY else order1
            )

            # Обновляем балансы
            await OrderService.update_balances(order1, order2)
            
            return True
        return False
    
    @staticmethod
    async def update_balances(buy_order: Order, sell_order: Order, executed_qty: int, execution_price: int):
        """Обновление балансов после исполнения сделки"""
        instrument = await Instrument.get(ticker=buy_order.ticker)
        
        # Для покупателя: списываем деньги, зачисляем актив
        await Balance.filter(
            user_id=buy_order.user_id,
            instrument__ticker="RUB"  # Предполагаем рублевый баланс
        ).update(
            amount=F('amount') - execution_price * executed_qty,
            locked=F('locked') - (buy_order.price - execution_price) * executed_qty
        )
        
        await Balance.filter(
            user_id=buy_order.user_id,
            instrument=instrument
        ).update(
            amount=F('amount') + executed_qty
        )
        
        # Для продавца: списываем актив, зачисляем деньги
        await Balance.filter(
            user_id=sell_order.user_id,
            instrument=instrument
        ).update(
            amount=F('amount') - executed_qty,
            locked=F('locked') - executed_qty
        )
        
        await Balance.filter(
            user_id=sell_order.user_id,
            instrument__ticker="RUB"
        ).update(
            amount=F('amount') + execution_price * executed_qty
        )

