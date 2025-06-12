from tortoise.models import Model
from tortoise import fields
import uuid
from app.services.api_key import generate_api_key

class User(Model):
    id = fields.UUIDField(pk=True, default = uuid.uuid4)
    name = fields.CharField(max_length=255)
    api_key = fields.CharField(max_length=255, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    role = fields.CharField(max_length=20, default="USER")  # USER/ADMIN

    class Meta:
        table = "users"

    @classmethod
    async def get_by_token(cls, token: str):
        """Get user by API token"""
        return await cls.get_or_none(api_key=token)