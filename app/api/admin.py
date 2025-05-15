from fastapi import APIRouter
from app.models import User

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

@router.delete("/user/{user_id}")
async def delete_user(user_id: int):
    await User.filter(id=user_id).delete()
    return {"success": True}