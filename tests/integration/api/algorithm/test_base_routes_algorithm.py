import pytest

from tests.test_config.classes.lists import BaseListsTest
from tests.test_config.classes.routes import BaseRoutesTest
from tests.test_config.utils.constants import Roles
from tests.test_config.utils.routes_utils import get_protected_routes

import tests.test_config.params.routes.algorithm as params


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
