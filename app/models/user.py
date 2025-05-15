from tortoise.models import Model
from tortoise import fields

class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    api_key = fields.CharField(max_length=36, unique=True)
    role = fields.CharField(max_length=20, default="user")  # user/admin

    class Meta:
        table = "users"