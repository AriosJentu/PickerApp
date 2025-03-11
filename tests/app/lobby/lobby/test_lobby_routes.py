import pytest

from fastapi import Response

from httpx import AsyncClient

from app.enums.user import UserRole
from app.enums.lobby import LobbyStatus

from tests.types import InputData
from tests.constants import Roles
from tests.classes.routes import BaseRoutesTest
from tests.classes.lists import BaseListsTest
from tests.factories.general_factory import GeneralFactory

import tests.params.routes.lobby as params
from tests.params.routes.common import get_exists_status_error_params, get_user_creator_access_error_params
from tests.utils.routes_utils import get_protected_routes


@pytest.mark.usefixtures("client_async")
@pytest.mark.parametrize("protected_route", get_protected_routes(params.ROUTES), indirect=True)
class TestLobbyRoutes(BaseRoutesTest):
    pass


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("create_test_lobbies")
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", params.LOBBY_FILTER_DATA)
class TestLobbyLists(BaseListsTest):
    route = "/api/v1/lobby/list"
    route_count = "/api/v1/lobby/list-count"
    obj_type = "lobbies"


@pytest.mark.asyncio
@pytest.mark.parametrize("lobby_data, expected_status, error_substr", params.LOBBY_DATA_STATUS_ERROR)
@pytest.mark.parametrize("algorithm_exists, expected_status_algorithm, error_algorithm_substr", get_exists_status_error_params("Algorithm"))
@pytest.mark.parametrize("role", Roles.LIST)
async def test_create_lobby(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        lobby_data: InputData,
        algorithm_exists: bool,
        expected_status: int,
        expected_status_algorithm: int,
        error_substr: str,
        error_algorithm_substr: str,
        role: UserRole
):

    route = "/api/v1/lobby/"

    base_user_data = await general_factory.create_base_user(role)
    algorithm_data = await general_factory.create_conditional_algorithm(base_user_data.user, algorithm_exists)

    lobby_data["host_id"] = base_user_data.user.id
    lobby_data["algorithm_id"] = algorithm_data.id

    response: Response = await client_async.post(route, json=lobby_data, headers=base_user_data.headers)

    json_data = response.json()
    if expected_status != 200:
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        message = json_data["detail"][0]["msg"]
        assert error_substr in str(message), f"Expected error '{error_substr}', got {message}"
        return
    
    assert response.status_code == expected_status_algorithm, f"Expected {expected_status_algorithm}, got {response.status_code}"
    if not algorithm_exists:
        assert error_algorithm_substr in str(json_data["detail"]), f"Expected error '{error_algorithm_substr}', got {json_data['detail']}"
        return

    assert json_data["name"] == lobby_data["name"], "Lobby name does not match"
    assert json_data["host"]["id"] == base_user_data.user.id, "User ID does not match"
    assert json_data["algorithm"]["id"] == algorithm_data.id, "Algorithm ID does not match"
    assert json_data["status"] == LobbyStatus.ACTIVE, "Lobby Status is not active"


@pytest.mark.asyncio
@pytest.mark.parametrize("lobby_exists, expected_status, error_substr", get_exists_status_error_params("Lobby"))
@pytest.mark.parametrize("role", Roles.LIST)
async def test_get_lobby_info(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        lobby_exists: bool,
        expected_status: int,
        error_substr: str,
        role: UserRole,
):
    
    base_user_data = await general_factory.create_base_user(role)
    lobby_data = await general_factory.create_conditional_lobby(base_user_data.user, lobby_exists)

    route = f"/api/v1/lobby/{lobby_data.id}"
    response: Response = await client_async.get(route, headers=base_user_data.headers)

    json_data = response.json()
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
    if not lobby_exists:
        assert error_substr in str(json_data["detail"]), f"Expected '{error_substr}', got: {json_data['detail']}"
        return
    
    assert json_data["id"] == lobby_data.id, "Lobby ID does not match"
    assert json_data["host"]["id"] == base_user_data.user.id, "User ID does not match"
    assert json_data["algorithm"]["id"] == lobby_data.data.algorithm_id, "Algorithm ID does not match"


@pytest.mark.asyncio
@pytest.mark.parametrize("update_data, expected_status_update, error_substr_update", params.LOBBY_UPDATE_DATA_STATUS_ERROR)
@pytest.mark.parametrize("role, is_lobby_owner, expected_status_access, error_substr_access", get_user_creator_access_error_params("lobby"))
@pytest.mark.parametrize("lobby_exists, expected_status_exists, error_substr_exists", get_exists_status_error_params("Lobby"))
async def test_update_lobby(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        update_data: InputData,
        is_lobby_owner: bool,
        lobby_exists: bool,
        expected_status_update: int,
        expected_status_access: int,
        expected_status_exists: int,
        error_substr_update: str,
        error_substr_access: str,
        error_substr_exists: str,
        role: UserRole,
):

    base_user_data, base_creator_data = await general_factory.create_base_users_creator(role)
    creator = base_user_data.user if is_lobby_owner else base_creator_data.user
    lobby_data = await general_factory.create_conditional_lobby(creator, lobby_exists)
    
    route = f"/api/v1/lobby/{lobby_data.id}"
    response: Response = await client_async.put(route, json=update_data, headers=base_user_data.headers)

    json_data = response.json()
    if expected_status_update == 422:
        assert response.status_code == expected_status_update, f"Expected {expected_status_update}, got {response.status_code}"
        assert error_substr_update in str(json_data["detail"]), f"Expected validation error '{error_substr_update}', got: {json_data['detail']}"
        return

    if not lobby_exists:
        assert response.status_code == expected_status_exists, f"Expected {expected_status_exists}, got {response.status_code}"
        assert error_substr_exists in str(json_data["detail"]), f"Expected error '{error_substr_exists}', got: {json_data['detail']}"
        return

    if expected_status_access != 200:
        assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
        assert error_substr_access in str(json_data["detail"]), f"Expected error '{error_substr_access}', got: {json_data['detail']}"
        return

    assert response.status_code == expected_status_update, f"Expected {expected_status_update}, got {response.status_code}"
    if expected_status_update == 400:
        assert error_substr_update in str(json_data["detail"]), f"Expected error '{error_substr_update}', got: {json_data['detail']}"
        return

    if "name" in update_data:
        assert json_data["name"] == update_data["name"], "Lobby name was not updated"
        assert json_data["status"] == LobbyStatus.ACTIVE, f"Lobby status isn't Active, got {json_data['status']}"
    
    if "status" in update_data:
        assert json_data["status"] == update_data["status"], f"Lobby status isn't {update_data["status"]}, got {json_data["status"]}"


@pytest.mark.asyncio
@pytest.mark.parametrize("role, is_lobby_owner, expected_status_access, error_substr_access", get_user_creator_access_error_params("lobby"))
@pytest.mark.parametrize("lobby_exists, expected_status_lobby, error_substr_lobby", get_exists_status_error_params("Lobby"))
async def test_close_lobby(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        is_lobby_owner: bool,
        lobby_exists: bool,
        expected_status_access: int,
        expected_status_lobby: int,
        error_substr_access: str,
        error_substr_lobby: str,
        role: UserRole,
):

    base_user_data, base_creator_data = await general_factory.create_base_users_creator(role)
    creator = base_user_data.user if is_lobby_owner else base_creator_data.user
    lobby_data = await general_factory.create_conditional_lobby(creator, lobby_exists)

    route = f"/api/v1/lobby/{lobby_data.id}/close"
    response: Response = await client_async.put(route, headers=base_user_data.headers)
    json_data = response.json()

    if not lobby_exists:
        assert response.status_code == expected_status_lobby, f"Expected {expected_status_lobby}, got {response.status_code}"
        assert error_substr_lobby in str(json_data["detail"]), f"Expected error '{error_substr_lobby}', got: {json_data['detail']}"
        return

    if expected_status_access != 200:
        assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
        assert error_substr_access in str(json_data["detail"]), f"Expected error '{error_substr_access}', got: {json_data['detail']}"
        return

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert json_data["status"] == LobbyStatus.ARCHIVED, f"Lobby status isn't Archived, got {json_data['status']}"


@pytest.mark.asyncio
@pytest.mark.parametrize("role, is_lobby_owner, expected_status_access, error_substr_access", get_user_creator_access_error_params("lobby"))
@pytest.mark.parametrize("lobby_exists, expected_status_lobby, error_substr_lobby", get_exists_status_error_params("Lobby"))
async def test_delete_lobby(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        is_lobby_owner: bool,
        lobby_exists: bool,
        expected_status_access: int,
        expected_status_lobby: int,
        error_substr_access: str,
        error_substr_lobby: str,
        role: UserRole,
):

    base_user_data, base_creator_data = await general_factory.create_base_users_creator(role)
    creator = base_user_data.user if is_lobby_owner else base_creator_data.user
    lobby_data = await general_factory.create_conditional_lobby(creator, lobby_exists)

    route = f"/api/v1/lobby/{lobby_data.id}"
    response: Response = await client_async.delete(route, headers=base_user_data.headers)
    json_data = response.json()

    if not lobby_exists:
        assert response.status_code == expected_status_lobby, f"Expected {expected_status_lobby}, got {response.status_code}"
        assert error_substr_lobby in str(json_data["detail"]), f"Expected error '{error_substr_lobby}', got: {json_data['detail']}"
        return

    if expected_status_access != 200:
        assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
        assert error_substr_access in str(json_data["detail"]), f"Expected error '{error_substr_access}', got: {json_data['detail']}"
        return

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert json_data["id"] == lobby_data.id, f"Expected {lobby_data.id}, got {json_data['id']}"
    assert lobby_data.data.name in json_data["description"], f"Deleted lobby with incorrect name"
