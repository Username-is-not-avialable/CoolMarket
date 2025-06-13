#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
print(sys.path)

from app.models.user import User
from app.core.database import init_db
from app.services.api_key import generate_api_key

async def create_admin_account():
    await init_db()
    
    admin = await User.get_or_none(name="admin")
    if admin:
        print(f"Админ уже существует:\n"
              f"ID: {admin.id}\n"
              f"API_KEY: {admin.api_key}")
        return

    admin = await User.create(
        name="admin",
        role="ADMIN",
        api_key="3Ee0eiifWB8o6bcuJ9VJijYNRvSTyiNX"
    )
    
    print("Админ создан:\n"
          f"ID: {admin.id}\n"
          f"API_KEY: {admin.api_key}\n"
          "Сохраните ключ в надёжном месте!")

if __name__ == "__main__":
    asyncio.run(create_admin_account())