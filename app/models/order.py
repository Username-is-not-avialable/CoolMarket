from tortoise.models import Model
from tortoise import fields

class Order(Model):
    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="orders")
    instrument = fields.ForeignKeyField("models.Instrument", related_name="orders")
    direction = fields.CharField(max_length=4)  # "BUY" или "SELL"
    price = fields.IntField(null=True)  # NULL для рыночных ордеров
    quantity = fields.IntField()
    status = fields.CharField(max_length=20, default="NEW")

    class Meta:
        table = "orders"