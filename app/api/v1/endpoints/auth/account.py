from fastapi import APIRouter, Depends, status

from app.modules.auth.user.services.user import UserService
from app.modules.auth.user.services.current import CurrentUserService

from app.modules.auth.token.schemas import TokenResponse, TokenStatus
from app.modules.auth.user.access import RoleChecker
from app.modules.auth.user.models import User
from app.modules.auth.user.schemas import UserRead, UserUpdateSecure

from app.modules.auth.user.exceptions import (
    HTTPUserExceptionUsernameAlreadyExists,
    HTTPUserExceptionEmailAlreadyExists,
    HTTPUserInternalError
)


router = APIRouter()

@router.get("/", response_model=UserRead)
async def get_current_user_(
    current_user: User = Depends(RoleChecker.user)
):
    return current_user


@router.put("/", response_model=TokenResponse)
async def update_current_user_(
    user_update: UserUpdateSecure,
    current_user: User = Depends(RoleChecker.user),
    user_service: UserService = Depends(UserService)
): 
    if user_update.email: 
        user_by_email = await user_service.get_by_email(user_update.email)
        
        if user_by_email and user_by_email.id != current_user.id:
            raise HTTPUserExceptionEmailAlreadyExists()
    
    if user_update.username:
        user_by_username = await user_service.get_by_username(user_update.username) 
        
        if user_by_username and user_by_username.id != current_user.id:
            raise HTTPUserExceptionUsernameAlreadyExists()

    access_token, refresh_token = await user_service.update_with_tokens(current_user, user_update)
    return TokenResponse(access_token=access_token.token, refresh_token=refresh_token.token, token_type="bearer")


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user_(
    user_service: UserService = Depends(UserService),
    current_user_service: CurrentUserService = Depends(CurrentUserService)
):
    result = await user_service.delete(await current_user_service.get())
    if not result:
        raise HTTPUserInternalError("Delete user error")


@router.get("/check-token", response_model=TokenStatus)
async def check_current_user_token(
    current_user: User = Depends(RoleChecker.user)
):
    return TokenStatus(
        active=True,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        detail="Token is valid"
    )
