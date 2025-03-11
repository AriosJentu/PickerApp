from typing import Optional
from fastapi import Depends

from app.enums.user import UserRole
from app.models.auth.user import User
from app.core.user.user import get_current_user, get_current_user_refresh
from app.exceptions.user import (
    HTTPUserUnauthorized, 
    HTTPUserExceptionAccessDenied,
)


def process_has_access(
    user: User, 
    required_role: UserRole, 
    additional_condition: Optional[bool] = None,
    condition_type: str = "or",
    exception: Exception = HTTPUserExceptionAccessDenied
):

    if not user:
        raise HTTPUserUnauthorized()
    
    has_access = user.role.has_access(required_role)
    if additional_condition is None:
        if not has_access:
            raise exception(required_role)

    if condition_type == "or":
        if not (has_access or additional_condition):
            raise exception(required_role)
    else:
        if not (has_access and additional_condition):
            raise exception(required_role)


def process_has_access_or(
    user: User, 
    required_role: UserRole, 
    additional_condition: bool = True,
    exception: Exception = HTTPUserExceptionAccessDenied
):
    process_has_access(user, required_role, additional_condition, "or", exception)


def process_has_access_and(
    user: User, 
    required_role: UserRole, 
    additional_condition: bool = True,
    exception: Exception = HTTPUserExceptionAccessDenied
):
    process_has_access(user, required_role, additional_condition, "and", exception)


def check_role(required_role: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)):

        process_has_access(current_user, required_role)
        return current_user

    return role_checker


def check_role_refresh(required_role: UserRole):
    def role_checker_refresh(current_user: User = Depends(get_current_user_refresh)):

        process_has_access(current_user, required_role)
        return current_user

    return role_checker_refresh


check_user_regular_role = check_role(UserRole.USER)
check_user_moderator_role = check_role(UserRole.MODERATOR)
check_user_admin_role = check_role(UserRole.ADMIN)

check_user_regular_role_refresh = check_role_refresh(UserRole.USER)
check_user_moderator_role_refresh = check_role_refresh(UserRole.MODERATOR)
check_user_admin_role_refresh = check_role_refresh(UserRole.ADMIN)
