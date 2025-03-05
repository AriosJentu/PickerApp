from typing import Callable, Awaitable, Any

from app.enums.user import UserRole
from app.db.base import User


type AllowedRoles = tuple[UserRole, ...]
type InputData = dict[str, Any]
type OutputData = dict[str, Any]
type Routes = list[tuple[str, str, tuple[UserRole, ...]]]
type RouteBaseFixture = tuple[str, str, AllowedRoles]
type BaseObjectFixtureCallable = Callable[[tuple[Any, ...]], Any]
type BaseUserFixture = tuple[User, InputData]
type BaseUserFixtureTokens = tuple[User, str, str, InputData]
type BaseUserFixtureCallable = Callable[[UserRole], Awaitable[BaseUserFixture | BaseUserFixtureTokens]]
type BaseCreatorUsersFixture = tuple[User, User, InputData, InputData]
type BaseCreatorUsersFixtureCallable = Callable[[UserRole], Awaitable[BaseUserFixture, BaseUserFixture]]
type BaseCreatorAdditionalUsersFixture = tuple[User, User, User, InputData, InputData, InputData]
type BaseCreatorAdditionalUsersFixtureCallable = Callable[[UserRole], Awaitable[BaseUserFixture, BaseUserFixture, BaseUserFixture]]
