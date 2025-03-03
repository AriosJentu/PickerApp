from app.enums.user import UserRole


USERS_COUNT = 3
LOBBIES_COUNT = 5
TEAMS_COUNT = 5

class Roles:
    LIST = [UserRole.USER, UserRole.MODERATOR, UserRole.ADMIN]
    ALL_ROLES = (UserRole.USER, UserRole.MODERATOR, UserRole.ADMIN)
    MODERATORS = (UserRole.MODERATOR, UserRole.ADMIN)
    MODERATOR = (UserRole.MODERATOR, )
    ADMIN = (UserRole.ADMIN, )