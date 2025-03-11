import pytest

from tests.constants import Roles
from tests.classes.routes import BaseRoutesTest
from tests.classes.lists import BaseListsTest

import tests.params.routes.algorithm as params
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
