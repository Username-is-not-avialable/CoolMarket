from fastapi import APIRouter, Header, HTTPException
from app.models.user import User
from app.services.auth import get_user_by_token
from uuid import UUID

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

@router.delete("/user/{user_id}")
async def delete_user(
    user_id: str,
    authorization: str = Header(..., alias="Authorization"),
):
    # Проверяем токен и получаем пользователя
    admin_user = await get_user_by_token(authorization)
    
    # Проверяем, что пользователь - администратор
    if admin_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only admin users can perform this action"
        )
    
    # Удаляем целевого пользователя
    deleted_count = await User.filter(id=user_id).delete()
    
    if not deleted_count:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return {"success": True}

@router.delete("/user/")
async def delete_user(
    user_id: str,
    authorization: str = Header(..., alias="Authorization"),
):
    print("passed")