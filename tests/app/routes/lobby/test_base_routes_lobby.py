import pytest

from tests.constants import Roles
from tests.classes.routes import BaseRoutesTest
from tests.classes.lists import BaseListsTest

import tests.params.routes.lobby as params
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


@pytest.mark.usefixtures("client_async")
@pytest.mark.usefixtures("create_test_participants")
@pytest.mark.usefixtures("test_lobby_id")
@pytest.mark.parametrize("role", Roles.LIST)
@pytest.mark.parametrize("filter_params, expected_count", params.PARTICIPANTS_FILTER_DATA)
class TestLobbyParticipantLists(BaseListsTest):
    
    obj_type = "participants"
    @pytest.fixture(autouse=True)
    def setup_routes(self, test_lobby_id: int):
        self.route = f"/api/v1/lobby/{test_lobby_id}/participants"
        self.route_count = f"/api/v1/lobby/{test_lobby_id}/participants-count"
