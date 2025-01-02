from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.core.dependencies import get_oauth2_scheme
from app.core.security.password import (
    get_password_hash, 
    verify_password
)

from app.core.security.user import (
    get_user_by_username,
    get_users_last_token,
    deactivate_old_tokens_user,
    create_user_tokens,
    refresh_user_tokens,
    get_current_user,
    get_current_user_refresh,
    is_user_exist,
    create_user,
)

from app.core.security.decorators import regular

from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.schemas.auth import LogoutResponse
from app.schemas.token import TokenResponse

from app.exceptions.user import (
    HTTPUserExceptionUsernameAlreadyExists, 
    HTTPUserExceptionEmailAlreadyExists,
    HTTPUserExceptionIncorrectData,
    HTTPUserExceptionAlreadyLoggedIn
)


router = APIRouter()

@router.post("/register", response_model=UserRead)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_async_session)
):
    username_exists, email_exists = await is_user_exist(db, user)

    if username_exists:
        raise HTTPUserExceptionUsernameAlreadyExists()
    
    if email_exists:
        raise HTTPUserExceptionEmailAlreadyExists()
    
    return await create_user(db, user, get_password_hash)


@router.post("/login", response_model=TokenResponse)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
):
    user = await get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPUserExceptionIncorrectData()
    
    if await get_users_last_token(db, user):
        raise HTTPUserExceptionAlreadyLoggedIn()

    access_token, refresh_token = await create_user_tokens(db, user)
    return TokenResponse(access_token=access_token.token, refresh_token=refresh_token.token, token_type="bearer")


@router.post("/logout", status_code=200, response_model=LogoutResponse)
@regular
async def logout_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    await deactivate_old_tokens_user(db, current_user)
    return LogoutResponse()


@router.post("/refresh", response_model=TokenResponse)
@regular
async def refresh_tokens(
    current_user: User = Depends(get_current_user_refresh),
    refresh_token: str = Depends(get_oauth2_scheme()),
    db: AsyncSession = Depends(get_async_session)
):
    new_access_token, refresh_token = await refresh_user_tokens(db, current_user, refresh_token)
    return TokenResponse(access_token=new_access_token.token, refresh_token=refresh_token, token_type="bearer")
