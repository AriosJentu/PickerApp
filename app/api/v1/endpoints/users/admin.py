from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_async_session

from app.modules.auth.token.schemas import TokenCleanResponse
from app.modules.auth.token.service import drop_all_inactive_tokens
from app.modules.auth.user.access import RoleChecker
from app.modules.auth.user.models import User


router = APIRouter()

@router.delete("/clear-tokens", response_model=TokenCleanResponse)
async def clear_inactive_tokens_(
    current_user: User = Depends(RoleChecker.admin),
    db: AsyncSession = Depends(get_async_session)
):
    count = await drop_all_inactive_tokens(db)
    return TokenCleanResponse(detail=f"Removed {count} inactive tokens from base")
