import pytest

from fastapi import Response

@pytest.mark.asyncio
async def test_create_user(client_async, default_user_data):

    response: Response = await client_async.post("/api/v1/auth/register", json=default_user_data)

    assert response.status_code == 201
    json_data = response.json()
    assert json_data["username"] == "defaultuser"
    assert json_data["email"] == "defaultuser@example.com"
    assert json_data["role"] == "user"
