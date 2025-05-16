from tortoise.models import Model
from tortoise import fields
import uuid
from app.services.api_key import generate_api_key

class User(Model):
    id = fields.UUIDField(pk=True, default = uuid.uuid4)
    name = fields.CharField(max_length=255)
    api_key = fields.CharField(max_length=36, unique=True, default = generate_api_key)
    role = fields.CharField(max_length=20, default="USER")  # USER/ADMIN

    class Meta:
        table = "users"