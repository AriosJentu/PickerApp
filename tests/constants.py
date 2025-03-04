from typing import Final

from app.enums.user import UserRole


USERS_COUNT:        Final[int] = 3
ALGORITHMS_COUNT:   Final[int] = 8
LOBBIES_COUNT:      Final[int] = 5
TEAMS_COUNT:        Final[int] = 5
PARTICIPANTS_COUNT: Final[int] = 8

class Roles:
    LIST:       Final[list[UserRole]]       = [UserRole.USER, UserRole.MODERATOR, UserRole.ADMIN]
    ALL_ROLES:  Final[tuple[UserRole, ...]] = (UserRole.USER, UserRole.MODERATOR, UserRole.ADMIN)
    MODERATORS: Final[tuple[UserRole, ...]] = (UserRole.MODERATOR, UserRole.ADMIN)
    MODERATOR:  Final[tuple[UserRole, ...]] = (UserRole.MODERATOR, )
    ADMIN:      Final[tuple[UserRole, ...]] = (UserRole.ADMIN, )