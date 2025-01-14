import pytest

from fastapi import Response

from app.core.security.password import get_password_hash
from app.crud.crud_user import db_create_user
from app.db.base import User
from app.schemas.user import UserCreate


@pytest.mark.asyncio
async def test_get_current_user(client_async, db_async, default_user_data):

    user_create = UserCreate(**default_user_data)
    await db_create_user(
        db_async,
        User.from_create(user_create, get_password_hash)
    )

    response: Response = await client_async.post(
        "/api/v1/auth/login",
        data=default_user_data,
    )

    assert response.status_code == 200
    tokens = response.json()

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    response: Response = await client_async.get("/api/v1/account/", headers=headers)
    assert response.status_code == 200

    user_data = response.json()
    assert user_data["username"] == default_user_data["username"]
    assert user_data["email"] == default_user_data["email"]
    assert user_data["role"] == "user"

    response: Response = await client_async.get("/api/v1/account/")
    assert response.status_code == 401
    assert "Not authenticated" in str(response.json())


@pytest.mark.asyncio
async def test_delete_current_user(client_async, db_async, default_user_data):
    
    user_create = UserCreate(**default_user_data)
    await db_create_user(
        db_async,
        User.from_create(user_create, get_password_hash)
    )

    response: Response = await client_async.post(
        "/api/v1/auth/login",
        data=default_user_data,
    )

    assert response.status_code == 200
    tokens = response.json()

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    response: Response = await client_async.delete("/api/v1/account/", headers=headers)
    assert response.status_code == 204

    response = await client_async.delete("/api/v1/account/", headers=headers)
    assert response.status_code == 401
    assert "Authorization token is invalid or expired" in str(response.json())
