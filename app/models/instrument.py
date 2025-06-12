from tortoise import fields, models
import uuid

class Instrument(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    ticker = fields.CharField(max_length=10, unique=True)
    name = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "instruments"

    @classmethod
    async def get_by_ticker(cls, ticker: str):
        """Get instrument by ticker"""
        return await cls.get_or_none(ticker=ticker)