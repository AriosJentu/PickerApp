from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import SessionLocal


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
