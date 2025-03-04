import pytest

from fastapi import Response

from httpx import AsyncClient

from app.db.base import Algorithm
from app.enums.user import UserRole

from tests.types import (
    BaseObjectFixtureCallable,
    BaseUserFixtureCallable, 
    BaseCreatorUsersFixtureCallable, 
    InputData, 
    RouteBaseFixture
)
from tests.constants import Roles, ALGORITHMS_COUNT
from tests.utils.test_access import check_access_for_authenticated_users, check_access_for_unauthenticated_users
from tests.utils.test_lists import check_list_responces
from tests.utils.routes_utils import get_protected_routes
from tests.utils.common_fixtures import (
    test_base_user_from_role, 
    test_base_creator_users_from_role, 
    test_create_algorithm_from_data,
    protected_route
)


all_routes = [
    ("POST",    "/api/v1/algorithm/",            Roles.ALL_ROLES),
    ("GET",     "/api/v1/algorithm/list-count",  Roles.ALL_ROLES),
    ("GET",     "/api/v1/algorithm/list",        Roles.ALL_ROLES),
    ("GET",     "/api/v1/algorithm/1",           Roles.ALL_ROLES),
    ("PUT",     "/api/v1/algorithm/1",           Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/algorithm/1",           Roles.ALL_ROLES),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
@pytest.mark.parametrize("role", Roles.LIST)
async def test_algorithm_routes_access(
        client_async: AsyncClient,
        protected_route: RouteBaseFixture,
        test_base_user_from_role: BaseUserFixtureCallable,
        role: UserRole
):
    await check_access_for_authenticated_users(client_async, protected_route, test_base_user_from_role, role)


@pytest.mark.asyncio
@pytest.mark.parametrize("protected_route", get_protected_routes(all_routes), indirect=True)
async def test_algorithm_routes_require_auth(
        client_async: AsyncClient,
        protected_route: RouteBaseFixture,
):
    await check_access_for_unauthenticated_users(client_async, protected_route)


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize(
    "algorithm_data, expected_status, error_substr",
    [
        (
            {"name": "Valid Algorithm", "algorithm": "BB PP T", "teams_count": 2},
            200, ""
        ),
        (
            {"name": "Invalid Step", "algorithm": "MM FS P", "teams_count": 2},
            422, "Step 'MM' containings incorrect symbols"
        ),
        (
            {"name": "Wrong Step Size", "algorithm": "BBB PPP T", "teams_count": 2},
            422, "Size of the step 'BBB' must be equal to teams count"
        ),
        (
            {"name": "  ", "algorithm": "BB PP T", "teams_count": 2},
            422, "Algorithm name cannot be empty"
        ),
        (
            {"name": "Missing Algorithm", "algorithm": "", "teams_count": 2},
            422, "Algorithm should contain at least one step"
        ),
        (
            {"name": "Negative Teams Count", "algorithm": "BB PP T", "teams_count": -1},
            422, "Teams count should be in between 2 and 16"
        ),
        (
            {}, 
            422, "Field required"
        ),
        (
            {"name": "No Algorithm"}, 
            422, "Field required"
        ),
        (
            {"algorithm": "BB PP T"}, 
            422, "Field required"
        ),
        (
            {"name": "No Teams Count", "algorithm": "BB PP T"}, 
            422, "Field required"
        ),
    ]
)
async def test_create_algorithm(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        algorithm_data: InputData,
        expected_status: int,
        error_substr: str,
        role: UserRole,
):

    route = "/api/v1/algorithm/"
    user, headers = await test_base_user_from_role(role)

    algorithm_data["creator_id"] = user.id
    response: Response = await client_async.post(route, json=algorithm_data, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
    
    json_data = response.json()
    if expected_status != 200:
        assert error_substr in str(json_data["detail"]), f"Incorrect validation response: {json_data["detail"]}"
        return

    assert json_data["name"] == algorithm_data["name"], "Algorithm name does not match"
    assert json_data["algorithm"] == algorithm_data["algorithm"], "Algorithm script does not match"
    assert json_data["teams_count"] == algorithm_data["teams_count"], "Teams count does not match"
    assert json_data["creator"]["id"] == user.id, "Algorithm creator does not match"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize(
    "algorithm_exists, expected_status, error_substr",
    [
        (True,  200,    ""),
        (False, 404,    "Algorithm not found"),
    ]
)
async def test_get_algorithm_info(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        test_create_algorithm_from_data: BaseObjectFixtureCallable,
        role: UserRole,
        algorithm_exists: bool,
        expected_status: int,
        error_substr: str
):
    
    user, headers = await test_base_user_from_role(role)
    algorithm_id, algorithm = await test_create_algorithm_from_data(user, algorithm_exists)

    route = f"/api/v1/algorithm/{algorithm_id}"
    response: Response = await client_async.get(route, headers=headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    json_data = response.json()
    if not algorithm_exists:
        assert error_substr in json_data["detail"], f"Expected error message '{error_substr}', got: {json_data['detail']}"
        return

    assert json_data["id"] == algorithm_id, "Algorithm ID does not match"
    assert json_data["name"] == algorithm.name, "Algorithm name does not match"
    assert json_data["algorithm"] == algorithm.algorithm, "Algorithm script does not match"
    assert json_data["teams_count"] == algorithm.teams_count, "Algorithm teams count does not match"


# TODO: Update, because now I have `404` when data is empty
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "update_data, expected_status, error_substr",
    [
        (
            {"name": "Valid Algorithm", "algorithm": "BB PP T", "teams_count": 2},
            200, ""
        ),
        (
            {"name": "Invalid Step", "algorithm": "MM FS P", "teams_count": 2},
            422, "Step 'MM' containings incorrect symbols"
        ),
        (
            {"name": "Wrong Step Size", "algorithm": "BBB PPP T", "teams_count": 2},
            422, "Size of the step 'BBB' must be equal to teams count"
        ),
        (
            {"name": "  ", "algorithm": "BB PP T", "teams_count": 2},
            422, "Algorithm name cannot be empty"
        ),
        (
            {"name": "Missing Algorithm", "algorithm": "", "teams_count": 2},
            422, "Algorithm should contain at least one step"
        ),
        (
            {"name": "Negative Teams Count", "algorithm": "BB PP T", "teams_count": -1},
            422, "Teams count should be in between 2 and 16"
        ),
        (
            {}, 
            422, "Field required"
        ),
        (
            {"name": "No Algorithm"}, 
            422, "Field required"
        ),
        (
            {"algorithm": "BB PP T"}, 
            422, "Field required"
        ),
        (
            {"name": "No Teams Count", "algorithm": "BB PP T"}, 
            422, "Field required"
        ),
    ]
)
@pytest.mark.parametrize(
    "role, is_creator, expected_status_access, error_substr_access",
    [
        (UserRole.ADMIN,        False,  200,    ""),
        (UserRole.MODERATOR,    False,  200,    ""),
        (UserRole.USER,         True,   200,    ""),
        (UserRole.USER,         False,  403,    "No access to control algorithm"),
    ]
)
@pytest.mark.parametrize(
    "algorithm_exists, expected_status_exists, error_substr_exists",
    [
        (True,  200,    ""),
        (False, 404,    "Algorithm not found"),
    ]
)
async def test_update_algorithm(
        client_async: AsyncClient,
        test_base_creator_users_from_role: BaseCreatorUsersFixtureCallable,
        test_create_algorithm_from_data: BaseObjectFixtureCallable,
        role: UserRole,
        is_creator: bool,
        algorithm_exists: bool,
        expected_status_access: int,
        expected_status_exists: int,
        update_data: InputData,
        expected_status: int,
        error_substr: str,
        error_substr_access: str,
        error_substr_exists: str,
):
    user, headers, creator, _ = await test_base_creator_users_from_role(role)
    algorithm_id, _ = await test_create_algorithm_from_data(user if is_creator else creator, algorithm_exists)

    route = f"/api/v1/algorithm/{algorithm_id}"
    response: Response = await client_async.put(route, json=update_data, headers=headers)

    json_data = response.json()
    if expected_status != 200:
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        assert error_substr in str(json_data["detail"]), f"Expected validation error '{error_substr}', got: {json_data["detail"]}"
        return
    
    if not algorithm_exists:
        assert response.status_code == expected_status_exists, f"Expected {expected_status_exists}, got {response.status_code}"
        assert error_substr_exists in json_data["detail"], f"Expected error message '{error_substr_exists}', got: {json_data["detail"]}"
        return

    assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
    if expected_status_access != 200:
        assert error_substr_access in json_data["detail"], f"Expected error message '{error_substr_access}', got: {json_data["detail"]}"
        return
    
    assert json_data["name"] == update_data["name"], "Algorithm name was not updated"
    assert json_data["algorithm"] == update_data["algorithm"], "Algorithm script was not updated"
    assert json_data["teams_count"] == update_data["teams_count"], "Teams count was not updated"    


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role, is_creator, expected_status_access, error_substr_access",
    [
        (UserRole.ADMIN,        False,  200,    ""),
        (UserRole.MODERATOR,    False,  200,    ""),
        (UserRole.USER,         True,   200,    ""),
        (UserRole.USER,         False,  403,    "No access to control algorithm"),
    ]
)
@pytest.mark.parametrize(
    "algorithm_exists, expected_status_exists, error_substr_exists",
    [
        (True,  200,    ""),
        (False, 404,    "Algorithm not found"),
    ]
)
async def test_delete_algorithm(
        client_async: AsyncClient,
        test_base_creator_users_from_role: BaseCreatorUsersFixtureCallable,
        test_create_algorithm_from_data: BaseObjectFixtureCallable,
        role: UserRole,
        is_creator: bool,
        algorithm_exists: bool,
        expected_status_access: int,
        expected_status_exists: int,
        error_substr_access: str,
        error_substr_exists: str,
):

    user, headers, creator, _ = await test_base_creator_users_from_role(role)
    algorithm_id, algorithm = await test_create_algorithm_from_data(user if is_creator else creator, algorithm_exists)
    
    route = f"/api/v1/algorithm/{algorithm_id}"
    response: Response = await client_async.delete(route, headers=headers)

    json_data = response.json()
    if not algorithm_exists:
        assert response.status_code == expected_status_exists, f"Expected {expected_status_exists}, got {response.status_code}"
        assert error_substr_exists in str(json_data["detail"]), f"Expected error message '{error_substr_exists}', got: {json_data["detail"]}"
        return

    assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
    if expected_status_access != 200:
        assert error_substr_access in str(json_data["detail"]), f"Expected error message '{error_substr_access}', got: {json_data["detail"]}"
        return

    assert json_data["id"] == algorithm_id, "Algorithm ID is not correct"
    assert algorithm.name in json_data["description"], "Algorithm name is not in response description"


filter_data = [
    (None,                                  ALGORITHMS_COUNT),
    ({"id":             1},                 1),
    ({"name":           "2"},               1),
    ({"name":           "Test Algorithm"},  ALGORITHMS_COUNT),
    ({"teams_count":    2},                 ALGORITHMS_COUNT),
    ({"teams_count":    3},                 0),
    ({"sort_by":        "id"},              ALGORITHMS_COUNT),
    ({"sort_order":     "desc"},            ALGORITHMS_COUNT),
    ({"limit":          2},                 2),
    ({"offset":         1},                 ALGORITHMS_COUNT-1),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", filter_data)
async def test_get_algorithms_list_with_filters(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        create_test_algorithms: list[Algorithm],
        role: UserRole,
        filter_params: InputData,
        expected_count: int
):
    
    route = "/api/v1/algorithm/list"
    await check_list_responces(
        client_async, test_base_user_from_role, role, route, 
        expected_count=expected_count,
        is_total_count=False, 
        filter_params=filter_params,
        obj_type="algorithms"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", filter_data)
async def test_get_algorithms_list_count_with_filters(
        client_async: AsyncClient,
        test_base_user_from_role: BaseUserFixtureCallable,
        create_test_algorithms: list[Algorithm],
        role: UserRole,
        filter_params: InputData,
        expected_count: int
):
    
    route = "/api/v1/algorithm/list-count"
    await check_list_responces(
        client_async, test_base_user_from_role, role, route, 
        expected_count=expected_count,
        is_total_count=True, 
        filter_params=filter_params,
        obj_type="algorithms"
    )
