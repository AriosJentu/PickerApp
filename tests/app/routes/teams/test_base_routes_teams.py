import pytest

from tests.utils.constants import Roles
from tests.classes.routes import BaseRoutesTest
from tests.classes.lists import BaseListsTest

import tests.params.routes.team as params
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
