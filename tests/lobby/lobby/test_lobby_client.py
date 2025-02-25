from typing import Callable, Awaitable

import pytest

from fastapi import Response
from httpx import AsyncClient

from app.db.base import Lobby

type LobbyData = dict[str, str | int]
type CallableLobbyData = Callable[[int], Awaitable[LobbyData]]


@pytest.mark.asyncio
async def test_create_lobby(
        client_async: AsyncClient, 
        default_lobby_data: CallableLobbyData, 
        user_access_token: str
):
    
    headers = {"Authorization": f"Bearer {user_access_token}"}
    lobby_data = await default_lobby_data(1)

    response: Response = await client_async.post("/api/v1/lobby/", json=lobby_data, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data["name"] == lobby_data["name"]
    assert json_data["description"] == lobby_data["description"]
    assert json_data["algorithm"]["id"] == lobby_data["algorithm_id"]


@pytest.mark.asyncio
async def test_get_lobby_list(
        client_async: AsyncClient, 
        create_test_lobbies: list[Lobby], 
        user_access_token: str
):

    headers = {"Authorization": f"Bearer {user_access_token}"}
    response: Response = await client_async.get("/api/v1/lobby/list", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert len(json_data) == len(create_test_lobbies)
    for lobby in create_test_lobbies:
        assert any(l["id"] == lobby.id for l in json_data)


@pytest.mark.asyncio
async def test_get_lobby_by_id(
        client_async: AsyncClient, 
        test_lobby_id: int, 
        user_access_token: str
):

    headers = {"Authorization": f"Bearer {user_access_token}"}
    response: Response = await client_async.get(f"/api/v1/lobby/{test_lobby_id}", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data["id"] == test_lobby_id


@pytest.mark.asyncio
async def test_update_lobby_no_access(
        client_async: AsyncClient, 
        test_lobby_id: int, 
        user_access_token: str
):

    headers = {"Authorization": f"Bearer {user_access_token}"}
    update_data = {"name": "Updated Lobby Name", "description": "Updated Description"}

    response: Response = await client_async.put(f"/api/v1/lobby/{test_lobby_id}", json=update_data, headers=headers)
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"

    json_data = response.json()
    assert json_data["detail"] == "No access to control lobby"


@pytest.mark.asyncio
async def test_update_lobby(
        client_async: AsyncClient, 
        test_lobby_id: int, 
        admin_access_token: str
):

    headers = {"Authorization": f"Bearer {admin_access_token}"}
    update_data = {"name": "Updated Lobby Name", "description": "Updated Description"}

    response: Response = await client_async.put(f"/api/v1/lobby/{test_lobby_id}", json=update_data, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data["name"] == update_data["name"]
    assert json_data["description"] == update_data["description"]


@pytest.mark.asyncio
async def test_delete_lobby_no_access(
        client_async: AsyncClient, 
        test_lobby_id: int, 
        user_access_token: str
):

    headers = {"Authorization": f"Bearer {user_access_token}"}

    response: Response = await client_async.delete(f"/api/v1/lobby/{test_lobby_id}", headers=headers)
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"


@pytest.mark.asyncio
async def test_delete_lobby_no_access(
        client_async: AsyncClient, 
        test_lobby_id: int, 
        admin_access_token: str
):

    headers = {"Authorization": f"Bearer {admin_access_token}"}

    response: Response = await client_async.delete(f"/api/v1/lobby/{test_lobby_id}", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    response: Response = await client_async.get(f"/api/v1/lobby/{test_lobby_id}", headers=headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
