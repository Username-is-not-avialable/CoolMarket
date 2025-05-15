from tortoise.models import Model
from tortoise import fields

class Instrument(Model):
    ticker = fields.CharField(pk=True, max_length=10)  # "BTC", "MEMCOIN"
    name = fields.CharField(max_length=100)
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "instruments"