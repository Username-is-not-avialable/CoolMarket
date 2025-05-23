from fastapi import APIRouter
from app.models.user import User
from app.schemas.user import UserCreate

router = APIRouter(prefix="/api/v1/public", tags=["Public"])

@router.post("/register")
async def register(user_data: UserCreate):
    user = await User.create(name=user_data.name)
    return user