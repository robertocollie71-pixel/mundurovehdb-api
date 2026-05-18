from fastapi import Depends, HTTPException, Header
from typing import Annotated

async def get_user_access_level(
    x_access_level: Annotated[int, Header(alias="X-Access-Level")] = 1
) -> int:
    """Akceptuje wszystkie poziomy >= 1 (w tym 10 dla admina/policji)"""
    if x_access_level < 1:
        raise HTTPException(status_code=403, detail="Nieprawidłowy poziom dostępu")
    return x_access_level
