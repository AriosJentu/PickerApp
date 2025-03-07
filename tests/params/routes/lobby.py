from app.enums.lobby import LobbyStatus

from tests.constants import LOBBIES_COUNT


LOBBY_DATA_STATUS_ERROR = [
    ({"name":   "New Lobby"},   200,    ""),
    ({"name":   "   "},         422,    "Lobby name cannot be empty"),
    ({},                        422,    "Field required"),
]

LOBBY_UPDATE_DATA_STATUS_ERROR = [
    ({"name":   "Updated Lobby"},               200,    ""),
    ({"status": LobbyStatus.ARCHIVED},          200,    ""),
    ({"name":   "   "},                         422,    "Lobby name cannot be empty"),
    ({},                                        400,    "Lobby update data not provided"),
]

LOBBY_FILTER_DATA = [
    (None,                              LOBBIES_COUNT),
    ({"id":             1},             1),
    ({"name":           "2"},           1),
    ({"name":           "Test Lobby"},  LOBBIES_COUNT),
    ({"host_id":        0},             LOBBIES_COUNT),
    ({"host_id":        1},             0),
    ({"algorithm_id":   1},             LOBBIES_COUNT),
    ({"sort_by":        "id"},          LOBBIES_COUNT),
    ({"sort_order":     "desc"},        LOBBIES_COUNT),
    ({"limit":          2},             2),
    ({"offset":         1},             LOBBIES_COUNT-1),
]
