import pytest

from tests.test_config.classes.lists import BaseListsTest
from tests.test_config.classes.routes import BaseRoutesTest
from tests.test_config.utils.constants import Roles
from tests.test_config.utils.routes_utils import get_protected_routes

import tests.test_config.params.routes.users as params


@pytest.mark.usefixtures("client_async")
@pytest.mark.parametrize("protected_route", get_protected_routes(params.ROUTES), indirect=True)
class TestUserRoutes(BaseRoutesTest):
    pass


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("create_multiple_test_users_with_tokens")
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", params.USERS_FILTER_DATA_MULTIPLE)
class TestMultipleUsersLists(BaseListsTest):
    route = "/api/v1/users/list"
    route_count = "/api/v1/users/list-count"
    obj_type = "users"


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("create_test_users")
@pytest.mark.parametrize("role", Roles.LIST_USER)
@pytest.mark.parametrize("filter_params, expected_count", params.USERS_FILTER_DATA)
class TestBaseUsersLists(BaseListsTest):
    route = "/api/v1/users/list"
    route_count = "/api/v1/users/list-count"
    obj_type = "users"
