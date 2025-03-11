import pytest

from fastapi import Response

from httpx import AsyncClient

from app.enums.user import UserRole

from tests.types import InputData
from tests.constants import Roles
from tests.classes.routes import BaseRoutesTest
from tests.classes.lists import BaseListsTest
from tests.factories.general_factory import GeneralFactory

import tests.params.routes.algorithm as params
from tests.params.routes.common import get_exists_status_error_params, get_user_creator_access_error_params
from tests.utils.routes_utils import get_protected_routes


@pytest.mark.usefixtures("client_async")
@pytest.mark.parametrize("protected_route", get_protected_routes(params.ROUTES), indirect=True)
class TestAlgorithmRoutes(BaseRoutesTest):
    pass


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("create_test_algorithms")
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", params.ALGORITHM_FILTER_DATA)
class TestAlgorithmLists(BaseListsTest):
    route = "/api/v1/algorithm/list"
    route_count = "/api/v1/algorithm/list-count"
    obj_type = "algorithms"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("algorithm_data, expected_status, error_substr", params.ALGORITHM_DATA_STATUS_ERROR)
async def test_create_algorithm(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        algorithm_data: InputData,
        expected_status: int,
        error_substr: str,
        role: UserRole,
):

    route = "/api/v1/algorithm/"
    base_user_data = await general_factory.create_base_user(role)

    algorithm_data["creator_id"] = base_user_data.user.id
    response: Response = await client_async.post(route, json=algorithm_data, headers=base_user_data.headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
    
    json_data = response.json()
    if expected_status != 200:
        assert error_substr in str(json_data["detail"]), f"Incorrect validation response: {json_data["detail"]}"
        return

    assert json_data["name"] == algorithm_data["name"], "Algorithm name does not match"
    assert json_data["algorithm"] == algorithm_data["algorithm"], "Algorithm script does not match"
    assert json_data["teams_count"] == algorithm_data["teams_count"], "Teams count does not match"
    assert json_data["creator"]["id"] == base_user_data.user.id, "Algorithm creator does not match"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("algorithm_exists, expected_status, error_substr", get_exists_status_error_params("Algorithm"))
async def test_get_algorithm_info(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        algorithm_exists: bool,
        expected_status: int,
        error_substr: str,
        role: UserRole,
):
    
    base_user_data = await general_factory.create_base_user(role)
    algorithm_data = await general_factory.create_conditional_algorithm(base_user_data.user, algorithm_exists)

    route = f"/api/v1/algorithm/{algorithm_data.id}"
    response: Response = await client_async.get(route, headers=base_user_data.headers)
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"

    json_data = response.json()
    if not algorithm_exists:
        assert error_substr in json_data["detail"], f"Expected error message '{error_substr}', got: {json_data['detail']}"
        return

    assert json_data["id"] == algorithm_data.id, "Algorithm ID does not match"
    assert json_data["name"] == algorithm_data.data.name, "Algorithm name does not match"
    assert json_data["algorithm"] == algorithm_data.data.algorithm, "Algorithm script does not match"
    assert json_data["teams_count"] == algorithm_data.data.teams_count, "Algorithm teams count does not match"


@pytest.mark.asyncio
@pytest.mark.parametrize("update_data, expected_status_update, error_substr_update", params.ALGORITHM_DATA_STATUS_ERROR)
@pytest.mark.parametrize("role, is_creator, expected_status_access, error_substr_access", get_user_creator_access_error_params("algorithm"))
@pytest.mark.parametrize("algorithm_exists, expected_status_exists, error_substr_exists", get_exists_status_error_params("Algorithm"))
async def test_update_algorithm(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        update_data: InputData,
        is_creator: bool,
        algorithm_exists: bool,
        expected_status_update: int,
        expected_status_access: int,
        expected_status_exists: int,
        error_substr_update: str,
        error_substr_access: str,
        error_substr_exists: str,
        role: UserRole,
):
    
    base_user_data, base_creator_data = await general_factory.create_base_users_creator(role)
    creator = base_user_data.user if is_creator else base_creator_data.user
    algorithm_data = await general_factory.create_conditional_algorithm(creator, algorithm_exists)
    
    route = f"/api/v1/algorithm/{algorithm_data.id}"
    response: Response = await client_async.put(route, json=update_data, headers=base_user_data.headers)

    json_data = response.json()
    if expected_status_update == 422:
        assert response.status_code == expected_status_update, f"Expected {expected_status_update}, got {response.status_code}"
        assert error_substr_update in str(json_data["detail"]), f"Expected validation error '{error_substr_update}', got: {json_data['detail']}"
        return
    
    if not algorithm_exists:
        assert response.status_code == expected_status_exists, f"Expected {expected_status_exists}, got {response.status_code}"
        assert error_substr_exists in json_data["detail"], f"Expected error message '{error_substr_exists}', got: {json_data["detail"]}"
        return
    
    if expected_status_access != 200:
        assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
        assert error_substr_access in str(json_data["detail"]), f"Expected error '{error_substr_access}', got: {json_data['detail']}"
        return

    assert response.status_code == expected_status_update, f"Expected {expected_status_update}, got {response.status_code}"
    if expected_status_update == 400:
        assert error_substr_update in str(json_data["detail"]), f"Expected error '{error_substr_update}', got: {json_data['detail']}"
        return
    
    assert json_data["name"] == update_data["name"], "Algorithm name was not updated"
    assert json_data["algorithm"] == update_data["algorithm"], "Algorithm script was not updated"
    assert json_data["teams_count"] == update_data["teams_count"], "Teams count was not updated"    


@pytest.mark.asyncio
@pytest.mark.parametrize("role, is_creator, expected_status_access, error_substr_access", get_user_creator_access_error_params("algorithm"))
@pytest.mark.parametrize("algorithm_exists, expected_status_exists, error_substr_exists", get_exists_status_error_params("Algorithm"))
async def test_delete_algorithm(
        client_async: AsyncClient,
        general_factory: GeneralFactory,
        is_creator: bool,
        algorithm_exists: bool,
        expected_status_access: int,
        expected_status_exists: int,
        error_substr_access: str,
        error_substr_exists: str,
        role: UserRole,
):

    base_user_data, base_creator_data = await general_factory.create_base_users_creator(role)
    creator = base_user_data.user if is_creator else base_creator_data.user
    algorithm_data = await general_factory.create_conditional_algorithm(creator, algorithm_exists)
    
    route = f"/api/v1/algorithm/{algorithm_data.id}"
    response: Response = await client_async.delete(route, headers=base_user_data.headers)

    json_data = response.json()
    if not algorithm_exists:
        assert response.status_code == expected_status_exists, f"Expected {expected_status_exists}, got {response.status_code}"
        assert error_substr_exists in str(json_data["detail"]), f"Expected error message '{error_substr_exists}', got: {json_data["detail"]}"
        return

    assert response.status_code == expected_status_access, f"Expected {expected_status_access}, got {response.status_code}"
    if expected_status_access != 200:
        assert error_substr_access in str(json_data["detail"]), f"Expected error message '{error_substr_access}', got: {json_data["detail"]}"
        return

    assert json_data["id"] == algorithm_data.id, "Algorithm ID is not correct"
    assert algorithm_data.data.name in json_data["description"], "Algorithm name is not in response description"
