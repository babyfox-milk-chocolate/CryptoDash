from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import async_session
from app.db.models import User
from app.core.security import decode_token


'''
    логика тут такая: на каждый запрос создается отдельная 
    сессия в БД. get_db() открывает сессию, отдает ее через yield,
    а когда запрос обработан - контекстный менеджер async with 
    автоматически ее закрывает 

'''
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


# извлекаем bearer token из заголовка
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)

    # токен невалиден 
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired token'
        )

    user = await db.scalar(select(User).where(User.id == int(payload['sub'])))
    if not user:
        raise HTTPException(status_code=401, detail='User not found')

    return user 

