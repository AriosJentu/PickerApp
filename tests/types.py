from typing import Any

from app.enums.user import UserRole


type AllowedRoles = tuple[UserRole, ...]
type InputData = dict[str, Any]
type Routes = list[tuple[str, str, tuple[UserRole, ...]]]
type RouteBaseFixture = tuple[str, str, AllowedRoles]
