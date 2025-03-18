from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_async_session
from app.core.security.password import get_password_hash
from app.core.security.access import check_user_regular_role
from app.modules.auth.user.service import (
    get_current_user, 
    get_user_by_username, 
    get_user_by_email,
    update_user,
    delete_user,
)

from app.modules.auth.user.models import User
from app.modules.auth.user.schemas import UserRead, UserUpdateSecure
from app.modules.auth.token.schemas import TokenResponse, TokenStatus

from app.modules.auth.user.exceptions import (
    HTTPUserExceptionUsernameAlreadyExists,
    HTTPUserExceptionEmailAlreadyExists,
    HTTPUserInternalError
)


router = APIRouter()

@router.get("/", response_model=UserRead)
async def get_current_user_(
    current_user: User = Depends(check_user_regular_role)
):
    return current_user


@router.put("/", response_model=TokenResponse)
async def update_current_user_(
    user_update: UserUpdateSecure,
    current_user: User = Depends(check_user_regular_role),
    db: AsyncSession = Depends(get_async_session)
): 
    if user_update.email: 
        user_by_email = await get_user_by_email(db, user_update.email)
        
        if user_by_email and user_by_email.id != current_user.id:
            raise HTTPUserExceptionEmailAlreadyExists()
    
    if user_update.username:
        user_by_username = await get_user_by_username(db, user_update.username) 
        
        if user_by_username and user_by_username.id != current_user.id:
            raise HTTPUserExceptionUsernameAlreadyExists()

    access_token, refresh_token = await update_user(db, current_user, user_update, get_password_hash)
    return TokenResponse(access_token=access_token.token, refresh_token=refresh_token.token, token_type="bearer")


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user_(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    result = await delete_user(db, current_user)
    if not result:
        raise HTTPUserInternalError("Delete user error")


@router.get("/check-token", response_model=TokenStatus)
async def check_current_user_token(
    current_user: User = Depends(check_user_regular_role)
):
    return TokenStatus(
        active=True,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        detail="Token is valid"
    )
