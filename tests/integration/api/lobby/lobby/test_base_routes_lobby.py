import pytest

from tests.test_config.classes.lists import BaseListsTest
from tests.test_config.classes.routes import BaseRoutesTest
from tests.test_config.utils.constants import Roles
from tests.test_config.utils.routes_utils import get_protected_routes

import tests.test_config.params.routes.lobby as params


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
