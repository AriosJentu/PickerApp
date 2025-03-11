from app.enums.user import UserRole

from tests.constants import Roles, USERS_COUNT


ROUTES = [
    ("GET",     "/api/v1/users/list",       Roles.ALL_ROLES),
    ("GET",     "/api/v1/users/list-count", Roles.ALL_ROLES),
    ("GET",     "/api/v1/users/",           Roles.ALL_ROLES),
    ("PUT",     "/api/v1/users/",           Roles.ADMIN),
    ("DELETE",  "/api/v1/users/",           Roles.ADMIN),
    ("DELETE",  "/api/v1/users/tokens",     Roles.ADMIN),
]

USERS_NONEXISTANT_DATA = [
    {"get_user_id":     -1}, 
    {"get_username":    "non_existant_username"},
    {"get_email":       "nonexistant@blackhole.org"},
]

USERS_UPDATE_VALID_DATA = [
    {"email":       "new_email@example.com"},
    {"username":    "somenewname"},
    {"password":    "NewPassword123!"}
]

USERS_UPDATE_INVALID_DATA = [
    ({"username":   ""},                "Username must be at least 3 characters long."),
    ({"password":   "InvalidPassword"}, "Password must contain"),
    ({"email":      "invalid-email"},   "Invalid email format"),
]

USERS_FILTER_DATA_MULTIPLE = [
    (None,                                      USERS_COUNT+1),
    ({"id":         1},                         1),
    ({"username":   "testuser"},                USERS_COUNT+1),
    ({"sort_by":    "id"},                      USERS_COUNT+1),
    ({"sort_order": "desc"},                    USERS_COUNT+1),
    ({"limit":      2},                         2),
    ({"offset":     1},                         USERS_COUNT),
]

USERS_FILTER_DATA = [
    (None,                                      4),
    ({"id":         1},                         1),
    ({"role":       UserRole.USER.value},       2),
    ({"role":       UserRole.ADMIN.value},      1),
    ({"username":   "default"},                 1),
    ({"email":      "moderator@example.com"},   1),
    ({"sort_by":    "id"},                      4),
    ({"sort_order": "desc"},                    4),
    ({"limit":      2},                         2),
    ({"offset":     1},                         3),
]
