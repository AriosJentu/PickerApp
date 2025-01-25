from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.core.security.password import get_password_hash
from app.core.security.decorators import regular
from app.core.security.user import (
    get_current_user, 
    get_user_by_username, 
    get_user_by_email,
    update_user,
    delete_user,
)

from app.models.auth.user import User
from app.schemas.auth.user import UserRead, UserUpdateSecure
from app.schemas.auth.token import TokenResponse, TokenStatus

from app.exceptions.user import (
    HTTPUserExceptionUsernameAlreadyExists,
    HTTPUserExceptionEmailAlreadyExists,
)


router = APIRouter()

@router.get("/", response_model=UserRead)
@regular
async def get_current_user_(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.put("/", response_model=TokenResponse)
@regular
async def update_current_user_(
    user_update: UserUpdateSecure,
    current_user: User = Depends(get_current_user),
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
@regular
async def delete_current_user_(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    await delete_user(db, current_user)


@router.get("/check-token", response_model=TokenStatus)
@regular
async def check_current_user_token(
    current_user: User = Depends(get_current_user)
):
    return TokenStatus(
        active=True,
        username=current_user.username,
        email=current_user.email,
        detail="Token is valid"
    )