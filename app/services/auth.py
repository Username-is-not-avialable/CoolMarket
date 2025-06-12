from fastapi import Header, HTTPException, Depends
from app.models.user import User

async def get_user_by_token(
    authorization: str = Header(..., alias="Authorization")
) -> User:
    """Проверка токена и получение объекта пользователя."""
    if not authorization:
        raise HTTPException(
            status_code=422,
            detail="Отсутствие токена"
        )
    if not authorization.startswith("TOKEN "):
        raise HTTPException(
            status_code=401,
            detail="Формат токена: 'TOKEN ваш_токен'"
        )

    api_key = authorization.split(" ")[1]
    user = await User.get_or_none(api_key=api_key)
    
    if not user:
        raise HTTPException(
            status_code=403,
            detail="Нет пользователя с таким токеном"
        )
    
    return user