import pytest

from fastapi import Response

from httpx import AsyncClient

from app.db.base import LobbyParticipant
from app.enums.user import UserRole
from app.enums.lobby import LobbyParticipantRole

from tests.types import InputData, RouteBaseFixture
from tests.constants import Roles
from tests.factories.general_factory import GeneralFactory

import tests.params.routes.lobby_participant as params
from tests.params.routes.common import get_user_creator_access_error_params
from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users
from tests.utils.test_lists import check_list_responces
from tests.utils.routes_utils import get_protected_routes


all_routes = [
    ("GET",     "/api/v1/lobby/1/participants-count",   Roles.ALL_ROLES),
    ("GET",     "/api/v1/lobby/1/participants",         Roles.ALL_ROLES),
    ("POST",    "/api/v1/lobby/1/participants",         Roles.ALL_ROLES),
    ("PUT",     "/api/v1/lobby/1/participants/1",       Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/lobby/1/participants/1",       Roles.ALL_ROLES),
    ("POST",    "/api/v1/lobby/1/connect",              Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/lobby/1/leave",                Roles.ALL_ROLES),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
@pytest.mark.parametrize("role", Roles.LIST)
async def test_lobby_participants_routes_access(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        protected_route: RouteBaseFixture,
        role: UserRole
):
    await check_access_for_authenticated_users(client_async, general_factory, protected_route, role)


@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
async def test_lobby_participants_routes_require_auth(
        client_async: AsyncClient,
        protected_route: RouteBaseFixture,
):
    await check_access_for_unauthenticated_users(client_async, protected_route)


@pytest.mark.asyncio
@pytest.mark.parametrize("with_team", [True, False])
@pytest.mark.parametrize("role, is_lobby_owner, expected_status, error_substr", get_user_creator_access_error_params("lobby"))
async def test_add_participant(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        with_team: bool,
        is_lobby_owner: bool,
        expected_status: int,
        error_substr: str,
        role: UserRole,
):

    base_user_data, base_creator_data = await general_factory.create_base_users_creator(role)
    creator = base_user_data.user if is_lobby_owner else base_creator_data.user
    lobby_data = await general_factory.create_conditional_lobby(creator)
    team_data = await general_factory.create_conditional_team(lobby_data.data)

    route = f"/api/v1/lobby/{lobby_data.id}/participants"
    params = {"user_id": base_user_data.user.id}
    if with_team:
        params["team_id"] = team_data.id

    response: Response = await client_async.post(route, params=params, headers=base_user_data.headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    json_data = response.json()
    if expected_status != 200:
        assert error_substr in str(json_data["detail"]), f"Expected error '{error_substr}', got: {json_data['detail']}"
        return

    assert json_data["lobby"]["id"] == lobby_data.id, f"Lobby ID is not the same as participant added to"
    assert json_data["user"]["id"] == base_user_data.user.id, f"User ID is not the same as participant's"
    assert json_data["role"] == LobbyParticipantRole.SPECTATOR, f"Participant has incorrect role"

    if with_team:
        assert json_data["team"]["id"] == team_data.id, f"Team ID is not the same as participant added to"


# TODO: Update, because now I have `404` when data is empty
@pytest.mark.asyncio
@pytest.mark.parametrize("update_data", params.PARTICIPANTS_UPDATE_DATA) 
@pytest.mark.parametrize("role, is_lobby_owner, expected_status, error_substr", get_user_creator_access_error_params("lobby"))
async def test_edit_participant(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        update_data: InputData,
        is_lobby_owner: bool,
        expected_status: int,
        error_substr: str,
        role: UserRole,
):

    base_user_data, base_creator_data, base_additional_data = await general_factory.create_base_users_creator_aditional(role)
    creator = base_user_data.user if is_lobby_owner else base_creator_data.user
    lobby_data = await general_factory.create_conditional_lobby(creator)
    team_data = await general_factory.create_conditional_team(lobby_data.data)

    route_add = f"/api/v1/lobby/{lobby_data.id}/participants"
    params = {"user_id": base_additional_data.user.id, "team_id": team_data.id}
    
    initial_headers = base_user_data.headers if is_lobby_owner else base_creator_data.headers
    response: Response = await client_async.post(route_add, params=params, headers=initial_headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data["user"]["id"] == base_additional_data.user.id, f"Expected User ID {base_additional_data.user.id}, got {json_data["user"]["id"]}"
    participant_id = json_data["id"]

    route = f"/api/v1/lobby/{lobby_data.id}/participants/{participant_id}"
    response: Response = await client_async.put(route, json=update_data, headers=base_user_data.headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    json_data = response.json()
    if expected_status != 200:
        assert error_substr in str(json_data["detail"]), f"Expected error '{error_substr}', got: {json_data['detail']}"
        return

    assert json_data["lobby"]["id"] == lobby_data.id, f"Lobby ID is not the same as participant added to"
    assert json_data["user"]["id"] == base_additional_data.user.id, f"User ID is not the same as participant's"

    if "role" in update_data:
        assert json_data["role"] == update_data["role"], f"Role was not updated"

    if "team_id" in update_data and update_data["team_id"] is not None:
        assert json_data["team"]["id"] == update_data["team_id"], f"Team ID was not updated"

    if "team_id" in update_data and update_data["team_id"] is None:
        assert json_data["team"] == update_data["team_id"], f"Team was not nulled"

    if "is_active" in update_data:
        assert json_data["is_active"] == update_data["is_active"], f"Active state was not updated"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_connect_to_lobby(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        test_lobby_id: int,
        role: UserRole
):

    route = f"/api/v1/lobby/{test_lobby_id}/connect"
    base_user_data = await general_factory.create_base_user(role)

    response: Response = await client_async.post(route, headers=base_user_data.headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data["lobby"]["id"] == test_lobby_id, f"Expected Lobby ID {test_lobby_id}, got {json_data["lobby"]["id"]}"
    assert json_data["user"]["id"] == base_user_data.user.id, f"Expected User ID {base_user_data.user.id}, got {json_data["user"]["id"]}"

    
    response: Response = await client_async.post(route, headers=base_user_data.headers)
    assert response.status_code == 409, f"Expected 409, got {response.status_code}"
    
    json_data = response.json()
    assert json_data["detail"] == "User already in lobby", f"Expected that user already in lobby"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
async def test_leave_lobby(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        test_lobby_id: int,
        role: UserRole
):

    route = f"/api/v1/lobby/{test_lobby_id}/leave"
    route_connect = f"/api/v1/lobby/{test_lobby_id}/connect"
    base_user_data = await general_factory.create_base_user(role)

    await client_async.post(route_connect, headers=base_user_data.headers)
    
    response: Response = await client_async.delete(route, headers=base_user_data.headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data["lobby"]["id"] == test_lobby_id, f"Expected Lobby ID {test_lobby_id}, got {json_data["lobby"]["id"]}"
    assert json_data["user"]["id"] == base_user_data.user.id, f"Expected User ID {base_user_data.user.id}, got {json_data["user"]["id"]}"


    response: Response = await client_async.delete(route, headers=base_user_data.headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    json_data = response.json()
    assert json_data["detail"] == "Participant not found", f"Expected that participant already not in lobby"


@pytest.mark.asyncio
@pytest.mark.parametrize("role, is_lobby_owner, expected_status, error_substr", get_user_creator_access_error_params("lobby"))
async def test_kick_from_lobby(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        is_lobby_owner: bool,
        expected_status: int,
        error_substr: str,
        role: UserRole,
):

    base_user_data, base_creator_data, base_additional_data = await general_factory.create_base_users_creator_aditional(role)
    creator = base_user_data.user if is_lobby_owner else base_creator_data.user
    lobby_data = await general_factory.create_conditional_lobby(creator)

    route_add = f"/api/v1/lobby/{lobby_data.id}/participants"
    params = {"user_id": base_additional_data.user.id}
    
    initial_headers = base_user_data.headers if is_lobby_owner else base_creator_data.headers
    response: Response = await client_async.post(route_add, params=params, headers=initial_headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    json_data = response.json()
    assert json_data["user"]["id"] == base_additional_data.user.id, f"Expected User ID {base_additional_data.user.id}, got {json_data["user"]["id"]}"
    participant_id = json_data["id"]

    route = f"/api/v1/lobby/{lobby_data.id}/participants/{participant_id}"
    response: Response = await client_async.delete(route, headers=base_user_data.headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    if expected_status != 200:
        assert error_substr in str(response.json()["detail"]), f"Expected error '{error_substr}', got: {response.json()['detail']}"
        return 

    response: Response = await client_async.delete(route, headers=base_user_data.headers)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    json_data = response.json()
    assert json_data["detail"] == "Participant not found", f"Expected that participant already not in lobby"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", params.PARTICIPANTS_FILTER_DATA)
async def test_get_lobby_participants_with_filters(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        test_lobby_id: int,
        create_test_participants: list[LobbyParticipant],
        filter_params: InputData,
        expected_count: int,
        role: UserRole,
):
    
    route = f"/api/v1/lobby/{test_lobby_id}/participants"
    await check_list_responces(
        client_async, general_factory, role, route, 
        expected_count=expected_count,
        is_total_count=False, 
        filter_params=filter_params,
        obj_type="participants"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", params.PARTICIPANTS_FILTER_DATA)
async def test_get_lobby_participants_count_with_filters(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        test_lobby_id: int,
        create_test_participants: list[LobbyParticipant],
        filter_params: InputData,
        expected_count: int,
        role: UserRole,
):
    
    route = f"/api/v1/lobby/{test_lobby_id}/participants-count"
    await check_list_responces(
        client_async, general_factory, role, route, 
        expected_count=expected_count,
        is_total_count=True, 
        filter_params=filter_params,
        obj_type="participants"
    )
