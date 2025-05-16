# from fastapi import APIRouter, Depends, Header
# from app.models import User
# from app.services.auth import get_user_by_token


# router = APIRouter(prefix="/api/v1", tags=["User"])

# @router.get("/balance")
# async def get_balances(user: User = Depends(get_user_by_token)):
#     return {"RUB": 1000}