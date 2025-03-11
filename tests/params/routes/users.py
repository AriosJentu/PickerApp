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

USERS_EXIST_STATUS_ERROR = [
    (True,  200,    "",                 {}),
    (False, 404,    "No data provided", {}),
    (False, 404,    "User not found",   {"get_user_id":     -1}),
    (False, 404,    "User not found",   {"get_username":    "someunexistantname"}),
    (False, 404,    "User not found",   {"get_email":       "unexistant@example.com"}),
]

USERS_PARAMS_STATUS_EXISTS_ERROR = [
    ({"get_user_id":    1},                         200,    True,   ""),
    ({"get_username":   "testuser"},                200,    True,   ""),
    ({"get_email":      "testuser@example.com"},    200,    True,   ""),
    ({"get_user_id":    999},                       404,    False,  "User not found"),
    ({"get_username":   "nonexistent"},             404,    False,  "User not found"),
    ({"get_email":      "noemail@example.com"},     404,    False,  "User not found"),
]

USERS_UPDATE_DATA_STATUS_ERROR = [
    ({"email":          "new_email@example.com"},                   200, ""),
    ({"username":       "somenewname"},                             200, ""),
    ({"password":       "NewPassword123!"},                         200, ""),
    ({"username":       ""},                                        422, "Username must be at least 3 characters long."),
    ({"password":       "InvalidPassword"},                         422, "Password must contain"),
    ({"email":          "invalid-email"},                           422, "Invalid email format"),
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
