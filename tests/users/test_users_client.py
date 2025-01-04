import pytest

from fastapi import Response

@pytest.mark.asyncio
async def test_create_user(client_async):
    data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "SecurePassword1!"
    }

    response: Response = await client_async.post("/api/v1/auth/register", json=data)

    assert response.status_code == 201
    json_data = response.json()
    assert json_data["username"] == "testuser"
    assert json_data["email"] == "testuser@example.com"
    assert json_data["role"] == "user"
