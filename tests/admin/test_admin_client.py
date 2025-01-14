import pytest

from fastapi import Response


@pytest.mark.asyncio
async def test_clear_inactive_tokens(client_async, admin_access_token):
    headers = {"Authorization": f"Bearer {admin_access_token}"}

    response: Response = await client_async.delete("/api/v1/admin/clear-tokens", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert "inactive tokens from base" in str(json_data), f"Unexpected response data: {json_data}"
