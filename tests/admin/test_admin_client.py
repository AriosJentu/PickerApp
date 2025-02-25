import pytest

from fastapi import Response

from httpx import AsyncClient


@pytest.mark.asyncio
async def test_unable_clear_inactive_tokens(
        client_async: AsyncClient,
        user_access_token: str
):
    
    headers = {"Authorization": f"Bearer {user_access_token}"}

    response: Response = await client_async.delete("/api/v1/admin/clear-tokens", headers=headers)
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"

    json_data = response.json()
    assert "Access denied" in str(json_data), f"Permissions error"


@pytest.mark.asyncio
async def test_clear_inactive_tokens(
        client_async: AsyncClient, 
        admin_access_token: str
):
    
    headers = {"Authorization": f"Bearer {admin_access_token}"}

    response: Response = await client_async.delete("/api/v1/admin/clear-tokens", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert "inactive tokens from base" in str(json_data), f"Unexpected response data: {json_data}"
