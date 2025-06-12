from fastapi import APIRouter, HTTPException
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    # Check if user with this name already exists
    if await User.filter(name=user_data.name).exists():
        raise HTTPException(status_code=400, detail="User with this name already exists")
    
    # Create new user
    user = await User.create(
        name=user_data.name,
        api_key=str(uuid.uuid4())  # Generate random API key
    )
    
    return UserResponse(
        id=user.id,
        name=user.name,
        api_key=user.api_key
    )