from app.enums.user import UserRole

from tests.constants import Roles


ROUTES = [
    ("POST", "/api/v1/auth/register",   None),
    ("POST", "/api/v1/auth/login",      None),
    ("POST", "/api/v1/auth/logout",     Roles.ALL_ROLES),
    ("POST", "/api/v1/auth/refresh",    Roles.ALL_ROLES),
]

REGISTER_DATA_STATUS_RESPONSE = [
    (
        {"username": "defaultuser",     "email": "defaultuser@example.com",     "password": "SecurePassword1!"},
        201,
        {"username": "defaultuser",     "email": "defaultuser@example.com",     "role": "user"},
    ),
    (
        {"username": "a",               "email": "defaultuser@example.com",     "password": "SecurePassword1!"},
        422,
        {"detail": "Username must be at least 3 characters long"},
    ),
    (
        {"username": "defaultuser",     "email": "invalidemail",                "password": "SecurePassword1!"},
        422,
        {"detail": "An email address must have an @-sign"},
    ),
    (
        {"username": "defaultuser",     "email": "defaultuser@example.com",     "password": "123"},
        422,
        {"detail": "Password must be at least 8 characters long"},
    ),
]

LOGIN_CREATE_DATA_STATUS_RESPONSE = [
    (
        {"username": "testuser", "email": "test@example.com", "password": "SecurePassword1!", "role": UserRole.USER},
        {"username": "testuser", "password": "SecurePassword1!"},
        200,
        {"token_type": "bearer"},
    ),
    (
        {"username": "testuser", "email": "test@example.com", "password": "SecurePassword1!", "role": UserRole.USER},
        {"username": "testuser", "password": "WrongPassword"},
        401,
        {"detail": "Incorrect username or password"},
    ),
    (
        {"username": "nonexistent", "email": "nonexistent@example.com", "password": "SomePassword", "role": UserRole.USER},
        {"username": "nonexistent", "password": "SomePassword"},
        401,
        {"detail": "Incorrect username or password"},
    ),
]
