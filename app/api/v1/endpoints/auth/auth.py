from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_async_session
from app.dependencies.oauth import get_oauth2_scheme

from app.modules.auth.user.service_old import (
    get_user_by_username,
    get_users_last_token,
    deactivate_old_tokens_user,
    create_user_tokens,
    refresh_user_tokens,
    is_user_exist,
    create_user,
)

from app.core.security.token import jwt_is_token_expired

from app.modules.auth.auth.schemas import LogoutResponse
from app.modules.auth.auth.password import PasswordManager
from app.modules.auth.token.schemas import TokenResponse
from app.modules.auth.user.access import AccessControl, RoleChecker
from app.modules.auth.user.models import User
from app.modules.auth.user.schemas import UserCreate, UserRead
from app.modules.auth.user.validators import UserValidator

from app.modules.auth.user.exceptions import (
    HTTPUserExceptionUsernameAlreadyExists, 
    HTTPUserExceptionEmailAlreadyExists,
    HTTPUserExceptionIncorrectData,
    HTTPUserExceptionIncorrectFormData,
    HTTPUserExceptionAlreadyLoggedIn,
)


router = APIRouter()

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user_(
    user: UserCreate,
    db: AsyncSession = Depends(get_async_session)
):
    username_exists, email_exists = await is_user_exist(db, user)

    if username_exists:
        raise HTTPUserExceptionUsernameAlreadyExists()
    
    if email_exists:
        raise HTTPUserExceptionEmailAlreadyExists()
    
    return await create_user(db, user, PasswordManager.hash)


@router.post("/login", response_model=TokenResponse)
async def login_user_(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
):
    
    try:
        UserValidator.username(form_data.username)
        UserValidator.password(form_data.password)
    except ValueError as error:
        raise HTTPUserExceptionIncorrectFormData(str(error))

    user = await get_user_by_username(db, form_data.username)
    if not user or not PasswordManager.verify(form_data.password, user.password):
        raise HTTPUserExceptionIncorrectData()
    
    token = await get_users_last_token(db, user)
    if token and not jwt_is_token_expired(token) and not AccessControl.is_available_to_relogin():
        raise HTTPUserExceptionAlreadyLoggedIn()

    access_token, refresh_token = await create_user_tokens(db, user)
    return TokenResponse(access_token=access_token.token, refresh_token=refresh_token.token, token_type="bearer")


@router.post("/logout", response_model=LogoutResponse)
async def logout_user_(
    current_user: User = Depends(RoleChecker.user),
    db: AsyncSession = Depends(get_async_session)
):
    await deactivate_old_tokens_user(db, current_user)
    return LogoutResponse()


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens_(
    current_user: User = Depends(RoleChecker.user_refresh),
    refresh_token: str = Depends(get_oauth2_scheme()),
    db: AsyncSession = Depends(get_async_session)
):
    new_access_token, refresh_token = await refresh_user_tokens(db, current_user, refresh_token)
    return TokenResponse(access_token=new_access_token.token, refresh_token=refresh_token, token_type="bearer")
