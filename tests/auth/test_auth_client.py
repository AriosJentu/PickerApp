import pytest

from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession

from httpx import AsyncClient

from app.core.security.password import get_password_hash
from app.crud.auth.user import db_create_user
from app.db.base import User
from app.schemas.auth.user import UserCreate
from app.enums.user import UserRole


@pytest.mark.parametrize(
    "data, expected_status, expected_response",
    [
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
    ],
)
@pytest.mark.asyncio
async def test_create_user(
        client_async: AsyncClient, 
        data: dict[str, str], 
        expected_status: int, 
        expected_response: dict[str, str]
):

    response: Response = await client_async.post("/api/v1/auth/register", json=data)

    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
    json_data = response.json()

    if expected_status == 201:
        assert json_data["username"] == expected_response["username"]
        assert json_data["email"] == expected_response["email"]
        assert json_data["role"] == expected_response["role"]
    else:
        assert expected_response["detail"] in str(json_data)


@pytest.mark.parametrize(
    "data, expected_status, expected_response",
    [
        (
            {"username": "defaultuser",     "email": "defaultuser@example.com",     "password": "SecurePassword1!"},
            200,
            {"token_type": "bearer"},
        ),
        (
            {"username": "nonexistentuser", "email": "nonexistentuser@example.com", "password": "SecurePassword1!"},
            401,
            {"detail": "Incorrect username or password"},
        ),
        (
            {"username": "defaultuser",     "email": "defaultuser@example.com",     "password": "WrongPassword!"},
            401,
            {"detail": "Incorrect username or password"},
        ),
        (
            {"username": "a",               "email": "defaultuser@example.com",     "password": "SecurePassword1!"},
            422,
            {"detail": "Username must be at least 3 characters long"},
        ),
    ],
)
@pytest.mark.asyncio
async def test_login_user(
        client_async: AsyncClient, 
        db_async: AsyncSession, 
        data: dict[str, str], 
        expected_status: int, 
        expected_response: dict[str, str]
):

    creation_data = {"username": "defaultuser",  "email": "defaultuser@example.com", "password": "SecurePassword1!"}

    user_create = UserCreate(**creation_data)
    await db_create_user(
        db_async,
        User.from_create(user_create, get_password_hash)
    )

    response: Response = await client_async.post(
        "/api/v1/auth/login",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
    json_data = response.json()

    if expected_status == 200:
        assert "access_token" in json_data
        assert json_data["token_type"] == expected_response["token_type"]
    else:
        assert expected_response["detail"] in str(json_data)


@pytest.mark.asyncio
async def test_logout_user(
        client_async: AsyncClient, 
        db_async: AsyncSession, 
        default_user_data: dict[str, str | UserRole]
):

    user_create = UserCreate(**default_user_data)
    await db_create_user(
        db_async,
        User.from_create(user_create, get_password_hash)
    )

    response: Response = await client_async.post(
        "/api/v1/auth/login",
        data=default_user_data,
    )
    assert response.status_code == 200, f"Expected 200 for Login, got {response.status_code}"
    tokens = response.json()

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    response: Response = await client_async.post("/api/v1/auth/logout", headers=headers)
    assert response.status_code == 200, f"Expected 200 for Logout, got {response.status_code}"
    assert "Successfully logout" in str(response.json())

    response: Response = await client_async.post("/api/v1/auth/logout", headers=headers)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    assert "Authorization token is invalid or expired" in str(response.json())


@pytest.mark.asyncio
async def test_refresh_token(
        client_async: AsyncClient, 
        db_async: AsyncSession, 
        default_user_data: dict[str, str | UserRole]
):
    
    user_create = UserCreate(**default_user_data)
    await db_create_user(
        db_async,
        User.from_create(user_create, get_password_hash)
    )

    response: Response = await client_async.post(
        "/api/v1/auth/login",
        data=default_user_data,
    )
    assert response.status_code == 200, f"Expected 200 for Login, got {response.status_code}"
    tokens = response.json()

    headers = {"Authorization": f"Bearer {tokens['refresh_token']}"}
    response: Response = await client_async.post("/api/v1/auth/refresh", headers=headers)
    assert response.status_code == 200, f"Expected 200 for Refresh, got {response.status_code}"
    
    new_tokens = response.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens

    headers = {"Authorization": "Bearer invalid_refresh_token"}
    response = await client_async.post("/api/v1/auth/refresh", headers=headers)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    assert "Invalid authorization token" in str(response.json())
