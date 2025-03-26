from app.modules.auth.user.enums import UserRole

from tests.test_config.utils.constants import Roles


ROUTES = [
    ("POST", "/api/v1/auth/register",   None),
    ("POST", "/api/v1/auth/login",      None),
    ("POST", "/api/v1/auth/logout",     Roles.ALL_ROLES),
    ("POST", "/api/v1/auth/refresh",    Roles.ALL_ROLES),
]

REGISTER_USER_VALID_DATA = [
    {"username":    "firstuser",    "email":    "firstuser@example.com",    "password": "SecurePassword1!"},
    {"username":    "other_user",   "email":    "myname@example.com",       "password": "SecurePasswd123!"},
]

REGISTER_USER_INVALID_DATA = [
    ({"username":   "a",            "email":    "defaultuser@example.com",  "password": "SecurePassword1!"},    "Username must be at least 3 characters long"),
    ({"username":   "defaultuser",  "email":    "invalidemail",             "password": "SecurePassword1!"},    "An email address must have an @-sign"),
    ({"username":   "defaultuser",  "email":    "defaultuser@example.com",  "password": "123"},                 "Password must be at least 8 characters long"),
    ({"username":   "defaultuser",  "email":    "defaultuser@example.com",  "password": "abcdefghij"},          "Password must contain at least one uppercase letter"),
    ({"username":   "defaultuser",  "email":    "defaultuser@example.com",  "password": "ABCDEFGHIJ"},          "Password must contain at least one lowercase letter"),
    ({"username":   "defaultuser",  "email":    "defaultuser@example.com",  "password": "AbcdEfghIj"},          "Password must contain at least one digit"),
    ({"username":   "defaultuser",  "email":    "defaultuser@example.com",  "password": "NonSecurePasswd123"},  "Password must contain at least one special character"),
]

REGISTER_USER_DUPLICATE_DATA = [
    ("username",    400,    "User with this username already exists"),
    ("email",       400,    "User with this email already exists"),
]

LOGIN_USER_VALID_DATA = [
    {"username":    "firstuser",    "password": "SecurePassword1!"},
    {"username":    "other_user",   "password": "SecurePasswd123!"},
]

LOGIN_USER_INVALID_DATA = [
    ({"username":   "a"},                                               "Field required"),
    ({"username":   "a",            "password": "123"},                 "Username must be at least 3 characters long"),
    ({"username":   "defaultuser",  "password": "123"},                 "Password must be at least 8 characters long"),
    ({"username":   "defaultuser",  "password": "abcdefghij"},          "Password must contain at least one uppercase letter"),
    ({"username":   "defaultuser",  "password": "ABCDEFGHIJ"},          "Password must contain at least one lowercase letter"),
    ({"username":   "defaultuser",  "password": "AbcdEfghIj"},          "Password must contain at least one digit"),
    ({"username":   "defaultuser",  "password": "NonSecurePasswd123"},  "Password must contain at least one special character"),
]
