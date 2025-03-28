from typing import Optional, Callable
from dataclasses import dataclass
from fastapi import Depends

from app.core.config import settings

from app.modules.auth.user.enums import UserRole
from app.modules.auth.user.models import User
from app.modules.auth.user.services.current import CurrentUserService
from app.modules.auth.user.exceptions import HTTPUserUnauthorized, HTTPUserExceptionAccessDenied


@dataclass
class RoleCheckers:
    user: Callable
    moderator: Callable
    admin: Callable
    user_refresh: Callable
    moderator_refresh: Callable
    admin_refresh: Callable


class AccessControl:

    @staticmethod
    def is_available_to_relogin() -> bool:
        return bool(settings.AVALIABLE_TO_RELOGIN)


    @staticmethod
    def has_access(
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


    @classmethod
    def has_access_or(cls,
            user: User, 
            required_role: UserRole, 
            additional_condition: Optional[bool] = None,
            exception: Exception = HTTPUserExceptionAccessDenied
    ):
        cls.has_access(user, required_role, additional_condition, "or", exception)


    @classmethod
    def has_access_and(cls,
            user: User, 
            required_role: UserRole, 
            additional_condition: Optional[bool] = None,
            exception: Exception = HTTPUserExceptionAccessDenied
    ):
        cls.has_access(user, required_role, additional_condition, "and", exception)


    @classmethod
    def check_role(cls, required_role: UserRole):
        async def role_checker(current_user_service: CurrentUserService = Depends(CurrentUserService)):
            cls.has_access(await current_user_service.get(), required_role)
            return current_user_service

        return role_checker

    @classmethod
    def check_role_refresh(cls, required_role: UserRole):
        async def role_checker_refresh(current_user_service: CurrentUserService = Depends(CurrentUserService)):
            cls.has_access(await current_user_service.get_refresh(), required_role)
            return current_user_service

        return role_checker_refresh

    @classmethod
    def get_role_checkers(cls) -> RoleCheckers:
        return RoleCheckers(
            user=cls.check_role(UserRole.USER),
            moderator=cls.check_role(UserRole.MODERATOR),
            admin=cls.check_role(UserRole.ADMIN),
            user_refresh=cls.check_role_refresh(UserRole.USER),
            moderator_refresh=cls.check_role_refresh(UserRole.MODERATOR),
            admin_refresh=cls.check_role_refresh(UserRole.ADMIN),
        )

RoleChecker: RoleCheckers = AccessControl.get_role_checkers()
