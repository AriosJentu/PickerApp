from typing import Optional
from functools import wraps

from app.enums.user import UserRole
from app.models.auth.user import User
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


def role_required(required_role: UserRole):
    
    def decorator(func):
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
        
            current_user: User = kwargs.get("current_user")
            process_has_access(current_user, required_role)
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def regular(func):
    return role_required(UserRole.USER)(func)


def moderator(func):
    return role_required(UserRole.MODERATOR)(func)


def administrator(func):
    return role_required(UserRole.ADMIN)(func)
