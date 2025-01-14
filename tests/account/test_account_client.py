import pytest

from fastapi import Response

from httpx import AsyncClient

from app.enums.user import UserRole


@pytest.mark.asyncio
async def test_check_token(
        client_async: AsyncClient, 
        default_user_data: dict[str, str | UserRole], 
        user_access_token: str
):

    headers = {"Authorization": f"Bearer {user_access_token}"}
    response: Response = await client_async.get("/api/v1/account/check-token", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data["active"] is True, "Expected token state `Active`"
    assert json_data["username"] == default_user_data["username"], f"Expected username: {default_user_data["username"]}, got {json_data["username"]}"
    assert json_data["email"] == default_user_data["email"], f"Expected email: {default_user_data["email"]}, got {json_data["email"]}"
    assert json_data["detail"] == "Token is valid", f"Expected detail `Token is valid`"


@pytest.mark.asyncio
async def test_get_current_user(
        client_async: AsyncClient, 
        default_user_data: dict[str, str | UserRole], 
        user_access_token: str
):

    headers = {"Authorization": f"Bearer {user_access_token}"}
    response: Response = await client_async.get("/api/v1/account/", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    user_data = response.json()
    assert user_data["username"] == default_user_data["username"], f"Expected username: {default_user_data["username"]}, got {user_data["username"]}"
    assert user_data["email"] == default_user_data["email"], f"Expected email: {default_user_data["email"]}, got {user_data["email"]}"
    assert user_data["role"] == "user", f"Expected role: user, got {user_data["role"]}"

    response: Response = await client_async.get("/api/v1/account/")
    assert response.status_code == 401, f"Expected 401 for non-authenticated, got {response.status_code}"
    assert "Not authenticated" in str(response.json())


@pytest.mark.asyncio
async def test_get_current_user_admin(
        client_async: AsyncClient, 
        default_admin_data: dict[str, str | UserRole], 
        admin_access_token: str
):

    headers = {"Authorization": f"Bearer {admin_access_token}"}
    response: Response = await client_async.get("/api/v1/account/", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    user_data = response.json()
    assert user_data["username"] == default_admin_data["username"], f"Expected username: {default_admin_data["username"]}, got {user_data["username"]}"
    assert user_data["email"] == default_admin_data["email"], f"Expected email: {default_admin_data["email"]}, got {user_data["email"]}"
    assert user_data["role"] == "admin", f"Expected role: admin, got {user_data["role"]}"

    response: Response = await client_async.get("/api/v1/account/")
    assert response.status_code == 401, f"Expected 401 for non-authenticated, got {response.status_code}"
    assert "Not authenticated" in str(response.json())


@pytest.mark.asyncio
async def test_delete_current_user(
        client_async: AsyncClient, 
        user_access_token: str
):

    headers = {"Authorization": f"Bearer {user_access_token}"}
    response: Response = await client_async.delete("/api/v1/account/", headers=headers)
    assert response.status_code == 204, f"Expected 204, got {response.status_code}"

    response = await client_async.delete("/api/v1/account/", headers=headers)
    assert response.status_code == 401, f"Expected 401 for unexistant user, got {response.status_code}"
    assert "Authorization token is invalid or expired" in str(response.json())


@pytest.mark.asyncio
async def test_update_current_user(
        client_async: AsyncClient, 
        user_access_token: str
):
    
    headers = {"Authorization": f"Bearer {user_access_token}"}
    update_data = {"email": "updated_email@example.com"}

    response: Response = await client_async.put("/api/v1/account/", headers=headers, json=update_data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert "access_token" in json_data, "Response does not contain access_token"
    assert "refresh_token" in json_data, "Response does not contain refresh_token"

    assert json_data["token_type"] == "bearer", "Unexpected token_type"
    assert json_data["access_token"] != "", "access_token is empty"
    assert json_data["refresh_token"] != "", "refresh_token is empty"

    headers = {"Authorization": f"Bearer {json_data['access_token']}"}
    user_info: Response = await client_async.get("/api/v1/account/", headers=headers)
    assert user_info.status_code == 200, f"Expected 200, got {response.status_code}"
    
    user_data = user_info.json()
    assert user_data["email"] == update_data["email"]
