from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies.oauth import get_oauth2_scheme

from app.modules.auth.auth.schemas import LogoutResponse
from app.modules.auth.auth.password import PasswordManager

from app.modules.auth.token.services.user import UserTokenService
from app.modules.auth.token.schemas import TokenResponse
from app.modules.auth.token.utils import TokenManager

from app.modules.auth.user.access import AccessControl, RoleChecker
from app.modules.auth.user.services.current import CurrentUserService
from app.modules.auth.user.services.user import UserService
from app.modules.auth.user.schemas import UserCreate, UserRead

from app.modules.auth.user.exceptions import (
    HTTPUserExceptionUsernameAlreadyExists, 
    HTTPUserExceptionEmailAlreadyExists,
    HTTPUserExceptionIncorrectData,
    HTTPUserExceptionAlreadyLoggedIn,
)


router = APIRouter()

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user_(
    user: UserCreate,
    user_service: UserService = Depends(UserService)
):
    username_exists, email_exists = await user_service.is_exist(user)

    if username_exists:
        raise HTTPUserExceptionUsernameAlreadyExists()
    
    if email_exists:
        raise HTTPUserExceptionEmailAlreadyExists()
    
    return await user_service.create(user)


@router.post("/login", response_model=TokenResponse)
async def login_user_(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(UserService),
    user_token_service: UserTokenService = Depends(UserTokenService)
):
    user_service.validate_form_data(form_data)

    user = await user_service.get_by_username(form_data.username)
    if not user or not PasswordManager.verify(form_data.password, user.password):
        raise HTTPUserExceptionIncorrectData()
    
    token = await user_token_service.get_last_token(user)
    if token and not TokenManager.is_token_expired(token.token) and not AccessControl.is_available_to_relogin():
        raise HTTPUserExceptionAlreadyLoggedIn()

    access_token, refresh_token = await user_token_service.create_tokens(user)
    return TokenResponse(access_token=access_token.token, refresh_token=refresh_token.token, token_type="bearer")


@router.post("/logout", response_model=LogoutResponse)
async def logout_user_(
    current_user_service: CurrentUserService = Depends(RoleChecker.user),
    user_token_service: UserTokenService = Depends(UserTokenService)
):
    await user_token_service.deactivate_old_tokens(await current_user_service.get())
    return LogoutResponse()


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens_(
    current_user_service: CurrentUserService = Depends(RoleChecker.user_refresh),
    refresh_token: str = Depends(get_oauth2_scheme()),
    user_token_service: UserTokenService = Depends(UserTokenService)
):
    new_access_token, refresh_token = await user_token_service.refresh_tokens(await current_user_service.get_refresh(), refresh_token)
    return TokenResponse(access_token=new_access_token.token, refresh_token=refresh_token, token_type="bearer")
