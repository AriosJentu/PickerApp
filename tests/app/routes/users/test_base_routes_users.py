import pytest

from tests.utils.constants import Roles
from tests.classes.routes import BaseRoutesTest
from tests.classes.lists import BaseListsTest

import tests.params.routes.users as params
from tests.utils.routes_utils import get_protected_routes


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
