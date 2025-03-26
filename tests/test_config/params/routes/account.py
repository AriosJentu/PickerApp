from tests.test_config.utils.constants import Roles


ROUTES = [
    ("GET",     "/api/v1/account/",             Roles.ALL_ROLES),
    ("PUT",     "/api/v1/account/",             Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/account/",             Roles.ALL_ROLES),
    ("GET",     "/api/v1/account/check-token",  Roles.ALL_ROLES),
]

UPDATE_USER_DATA_VALID = [
    {"email":       "updated_email@example.com"},
    {"username":    "newusername"},
    {"password":    "NewPassword123!"},
    {"email":       "updated_email@example.com",    "username": "newusername"}
]

UPDATE_USER_DATA_INVALID = [
    ({"email":      "invalid-email"},                       "Invalid email format"),
    ({"username":   ""},                                    "Username must be at least 3 characters long"),
    ({"password":   "weakpass"},                            "Password must contain"),
    ({"email":      "invalid-email",    "username": ""},    "Username must be at least 3 characters long"),
]

UPDATE_USER_DATA_DUPLICATES = [
    {"email":       "updated_email@example.com",    "username": "newusername"}
]

UPDATE_USER_DUPLICATE_EMAIL_EXPECT_ERROR = [
    (False, 200,    ""),
    (True,  400,    "User with this email already exists"),
]

UPDATE_USER_DUPLICATE_USERNAME_EXPECT_ERROR = [
    (False, 200,    ""),
    (True,  400,    "User with this username already exists"),
]
