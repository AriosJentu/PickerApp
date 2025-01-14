import pytest

from httpx import AsyncClient

from app.db.base import User
from app.enums.user import UserRole


@pytest.mark.asyncio
async def test_get_users_list(
        client_async: AsyncClient,
        create_test_users: list[User],
        user_access_token: str
):
    headers = {"Authorization": f"Bearer {user_access_token}"}
    response = await client_async.get("/api/v1/users/list", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    json_data = response.json()
    assert len(json_data) == len(create_test_users)


@pytest.mark.asyncio
async def test_get_users_list_filtered(
        client_async: AsyncClient, 
        create_test_users: list[User],
        user_access_token: str
):
    headers = {"Authorization": f"Bearer {user_access_token}"}
    response = await client_async.get("/api/v1/users/list", params={"role": 1}, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    json_data = response.json()
    assert all(user["role"] == "user" for user in json_data)
