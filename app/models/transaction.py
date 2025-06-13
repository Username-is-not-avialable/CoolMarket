from tortoise.models import Model
from tortoise import fields
import uuid

class Transaction(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    buyer_id = fields.UUIDField()
    seller_id = fields.UUIDField()
    instrument = fields.ForeignKeyField("models.Instrument")
    price = fields.IntField()
    quantity = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    order_buy = fields.ForeignKeyField("models.Order", related_name="buy_transactions")
    order_sell = fields.ForeignKeyField("models.Order", related_name="sell_transactions")

    class Meta:
        table = "transactions"