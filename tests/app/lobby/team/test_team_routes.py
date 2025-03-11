import pytest

from fastapi import Response

from httpx import AsyncClient

from app.db.base import Team
from app.enums.user import UserRole

from tests.types import InputData
from tests.constants import Roles
from tests.classes.routes import BaseRoutesTest
from tests.classes.lists import BaseListsTest
from tests.factories.general_factory import GeneralFactory

import tests.params.routes.team as params
from tests.params.routes.common import get_exists_status_error_params, get_user_creator_access_error_params
from tests.utils.test_lists import check_list_responces
from tests.utils.routes_utils import get_protected_routes


@pytest.mark.usefixtures("client_async")
@pytest.mark.parametrize("protected_route", get_protected_routes(params.ROUTES), indirect=True)
class TestTeamRoutes(BaseRoutesTest):
    pass


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("create_test_teams")
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", params.TEAM_FILTER_DATA)
class TestTeamLists(BaseListsTest):
    route = "/api/v1/teams/list"
    route_count = "/api/v1/teams/list-count"
    obj_type = "teams"


@pytest.mark.asyncio
@pytest.mark.parametrize("team_data, expected_status_team, error_substr_team", params.TEAM_DATA_STATUS_ERROR)
@pytest.mark.parametrize("role, is_lobby_owner, expected_status_access, error_substr_access", get_user_creator_access_error_params("team"))
@pytest.mark.parametrize("lobby_exists, expected_status_lobby, error_substr_lobby", get_exists_status_error_params("Lobby"))
async def test_create_team(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        team_data: InputData,
        expected_status_team: int,
        error_substr_team: str,
        role: UserRole,
        is_lobby_owner: bool,
        expected_status_access: int,
        error_substr_access: str,
        lobby_exists: bool,
        expected_status_lobby: int,
        error_substr_lobby: str
):

    route = "/api/v1/teams/"

    base_user_data, base_creator_data = await general_factory.create_base_users_creator(role)
    creator = base_user_data.user if is_lobby_owner else base_creator_data.user
    lobby_data = await general_factory.create_conditional_lobby(creator, lobby_exists)
    team_data["lobby_id"] = lobby_data.id

    response: Response = await client_async.post(route, json=team_data, headers=base_user_data.headers)
    json_data = response.json()

    if expected_status_team != 200:
        assert response.status_code == expected_status_team, f"Expected {expected_status_team}, got {response.status_code}"
        assert error_substr_team in json_data["detail"][0]["msg"], f"Validation error mismatch: {json_data['detail'][0]['msg']}"
        return

    if expected_status_lobby != 200:
        assert response.status_code == expected_status_lobby, f"Expected {expected_status_lobby}, got {response.status_code}"
        assert error_substr_lobby in json_data["detail"], f"Expected error message '{error_substr_lobby}', got: {json_data['detail']}"
        return

    assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
    if expected_status_access != 200:
        assert error_substr_access in json_data["detail"], f"Expected error message '{error_substr_access}', got: {json_data['detail']}"
        return

    assert json_data["name"] == team_data["name"], "Team name does not match"
    assert json_data["lobby"]["id"] == team_data["lobby_id"], "Lobby ID does not match"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("team_exists, expected_status, error_substr", get_exists_status_error_params("Team"))
async def test_get_team_info(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        role: UserRole,
        team_exists: bool,
        expected_status: int,
        error_substr: str
):
    
    base_user_data = await general_factory.create_base_user(role)
    lobby_data = await general_factory.create_conditional_lobby(base_user_data.user)
    team_data = await general_factory.create_conditional_team(lobby_data.data, team_exists)
    
    route = f"/api/v1/teams/{team_data.id}"
    response: Response = await client_async.get(route, headers=base_user_data.headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    json_data = response.json()
    if not team_exists:
        assert error_substr in json_data["detail"], f"Expected error message '{error_substr}', got: {json_data['detail']}"
        return

    assert json_data["id"] == team_data.id, "Team ID does not match"
    assert json_data["name"] == team_data.data.name, "Team name does not match"
    assert json_data["lobby"]["id"] == lobby_data.id, "Lobby ID associated with team is incorrect"


@pytest.mark.asyncio
@pytest.mark.parametrize("update_data, expected_status_update, error_substr_update", params.TEAM_UPDATE_DATA_STATUS_ERROR)
@pytest.mark.parametrize("role, is_lobby_owner, expected_status_access, error_substr_access", get_user_creator_access_error_params("team"))
@pytest.mark.parametrize("team_exists, expected_status_exists, error_substr_exists", get_exists_status_error_params("Team"))
async def test_update_team(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        update_data: InputData,
        is_lobby_owner: bool,
        team_exists: bool,
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
    lobby_data = await general_factory.create_conditional_lobby(creator)
    team_data = await general_factory.create_conditional_team(lobby_data.data, team_exists)

    route = f"/api/v1/teams/{team_data.id}"
    response: Response = await client_async.put(route, json=update_data, headers=base_user_data.headers)
    
    json_data = response.json()
    if expected_status_update == 422:
        assert response.status_code == expected_status_update, f"Expected {expected_status_update}, got {response.status_code}"
        assert error_substr_update in str(json_data["detail"]), f"Expected validation error '{error_substr_update}', got: {json_data['detail']}"
        return

    if not team_exists:
        assert response.status_code == expected_status_exists, f"Expected {expected_status_exists}, got {response.status_code}"
        assert error_substr_exists in json_data["detail"], f"Expected error message '{error_substr_exists}', got: {json_data['detail']}"
        return

    if expected_status_access != 200:
        assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
        assert error_substr_access in str(json_data["detail"]), f"Expected error '{error_substr_access}', got: {json_data['detail']}"
        return

    assert response.status_code == expected_status_update, f"Expected {expected_status_update}, got {response.status_code}"
    if expected_status_update == 400:
        assert error_substr_update in str(json_data["detail"]), f"Expected error '{error_substr_update}', got: {json_data['detail']}"
        return

    assert json_data["name"] == update_data["name"], "Team name was not updated"


@pytest.mark.asyncio
@pytest.mark.parametrize("role, is_lobby_owner, expected_status_access, error_substr_access", get_user_creator_access_error_params("team"))
@pytest.mark.parametrize("team_exists, expected_status_exists, error_substr_exists", get_exists_status_error_params("Team"))
async def test_delete_team(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        is_lobby_owner: bool,
        team_exists: bool,
        expected_status_access: int,
        expected_status_exists: int,
        error_substr_access: str,
        error_substr_exists: str,
        role: UserRole,
):

    base_user_data, base_creator_data = await general_factory.create_base_users_creator(role)
    creator = base_user_data.user if is_lobby_owner else base_creator_data.user
    lobby_data = await general_factory.create_conditional_lobby(creator)
    team_data = await general_factory.create_conditional_team(lobby_data.data, team_exists)

    route = f"/api/v1/teams/{team_data.id}"
    response: Response = await client_async.delete(route, headers=base_user_data.headers)

    json_data = response.json()
    if expected_status_exists != 200:
        assert response.status_code == expected_status_exists, f"Expected {expected_status_exists}, got {response.status_code}"
        assert error_substr_exists in json_data["detail"], f"Expected error message '{error_substr_exists}', got: {json_data['detail']}"
        return

    assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
    if expected_status_access != 200:
        assert error_substr_access in json_data["detail"], f"Expected error message '{error_substr_access}', got: {json_data['detail']}"
        return

    assert json_data["description"] == f"Team '{team_data.data.name}' deleted successfully"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", params.TEAM_FILTER_DATA)
async def test_get_teams_list_with_filters(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        create_test_teams: list[Team],
        filter_params: InputData,
        expected_count: int,
        role: UserRole,
):
    
    route = "/api/v1/teams/list"
    await check_list_responces(
        client_async, general_factory, role, route, 
        expected_count=expected_count,
        is_total_count=False, 
        filter_params=filter_params,
        obj_type="teams"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", params.TEAM_FILTER_DATA)
async def test_get_teams_list_count_with_filters(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        create_test_teams: list[Team],
        filter_params: InputData,
        expected_count: int,
        role: UserRole,
):
    
    route = "/api/v1/teams/list-count"
    await check_list_responces(
        client_async, general_factory, role, route, 
        expected_count=expected_count,
        is_total_count=True, 
        filter_params=filter_params,
        obj_type="teams"
    )
