from tortoise import fields, models
from datetime import datetime
import uuid

class Order(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user_id = fields.UUIDField()
    status = fields.CharField(
        max_length=20,
        default="NEW",
        choices=[
            ("NEW", "New"),
            ("PARTIALLY_FILLED", "Partially Filled"),
            ("FILLED", "Filled"),
            ("CANCELLED", "Cancelled"),
            ("REJECTED", "Rejected")  # Для рыночных ордеров, которые не исполнились
        ]
    )
    body = fields.JSONField()
    filled = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_market = fields.BooleanField(default=False)

    class Meta:
        table = "orders"

        indexes = (
            ("status", "created_at"),  # Для поиска ордеров на исполнение
            ("user_id", "status"),     # Для истории ордеров пользователя
        )