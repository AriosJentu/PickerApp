from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.token import TokenCleanResponse

from app.models.user import User
from app.core.security.user import get_current_user
from app.core.security.decorators import administrator
from app.db.session import get_async_session

from app.core.security.token import drop_all_inactive_tokens


router = APIRouter()

@router.delete("/clear-tokens", response_model=TokenCleanResponse)
@administrator
async def clear_inactive_tokens(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    # print("Current user: ", current_user.role, current_user)
    count = await drop_all_inactive_tokens(db)
    
    return TokenCleanResponse(detail=f"Removed {count} inactive tokens from base")
