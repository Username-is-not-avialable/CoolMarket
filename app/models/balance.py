from tortoise.models import Model
from tortoise import fields

class Balance(Model):
    user = fields.ForeignKeyField("models.User", related_name="balances")
    instrument = fields.ForeignKeyField("models.Instrument", related_name="balances")
    amount = fields.BigIntField(default=0)  # Используем BigInt для избежания переполнения

    class Meta:
        table = "balances"
        unique_together = (("user", "instrument"),)  # Один баланс на пару user+instrument
        indexes = (("user", "instrument"),)