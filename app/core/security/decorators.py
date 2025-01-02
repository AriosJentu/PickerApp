from functools import wraps

from app.enums.user import UserRole
from app.models.user import User
from app.exceptions.user import (
    HTTPUserUnauthorized, 
    HTTPUserExceptionAccessDenied
)

def role_required(required_role: UserRole):
    
    def decorator(func):
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
        
            current_user: User = kwargs.get("current_user")
            
            if not current_user:
                raise HTTPUserUnauthorized()
            
            if not current_user.role.has_access(required_role):
                raise HTTPUserExceptionAccessDenied(required_role)
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def regular(func):
    return role_required(UserRole.USER)(func)


def moderator(func):
    return role_required(UserRole.MODERATOR)(func)


def administrator(func):
    return role_required(UserRole.ADMIN)(func)

