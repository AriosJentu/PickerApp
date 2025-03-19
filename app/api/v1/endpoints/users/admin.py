from fastapi import APIRouter, Depends

from app.modules.auth.token.schemas import TokenCleanResponse
from app.modules.auth.token.services.token import TokenService
from app.modules.auth.user.access import RoleChecker
from app.modules.auth.user.services.current import CurrentUserService


router = APIRouter()

@router.delete("/clear-tokens", response_model=TokenCleanResponse)
async def clear_inactive_tokens_(
    current_user_service: CurrentUserService = Depends(RoleChecker.admin),
    token_service: TokenService = Depends(TokenService)
):
    count = await token_service.drop_all_inactive_tokens()
    return TokenCleanResponse(detail=f"Removed {count} inactive tokens from base")
