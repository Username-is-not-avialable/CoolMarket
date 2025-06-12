from tortoise import fields, models
from datetime import datetime
import uuid

class Order(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user_id = fields.UUIDField()
    status = fields.CharField(max_length=20, default="NEW")
    body = fields.JSONField()
    filled = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "orders"