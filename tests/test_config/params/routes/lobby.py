from app.modules.lobby.lobby.enums import LobbyStatus, LobbyParticipantRole

from tests.test_config.utils.constants import Roles, LOBBIES_COUNT, PARTICIPANTS_COUNT


ROUTES = [
    ("POST",    "/api/v1/lobby/",                       Roles.ALL_ROLES),
    ("GET",     "/api/v1/lobby/list-count",             Roles.ALL_ROLES),
    ("GET",     "/api/v1/lobby/list",                   Roles.ALL_ROLES),
    ("GET",     "/api/v1/lobby/1",                      Roles.ALL_ROLES),
    ("PUT",     "/api/v1/lobby/1",                      Roles.ALL_ROLES),
    ("PUT",     "/api/v1/lobby/1/close",                Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/lobby/1",                      Roles.ALL_ROLES),
    ("GET",     "/api/v1/lobby/1/participants-count",   Roles.ALL_ROLES),
    ("GET",     "/api/v1/lobby/1/participants",         Roles.ALL_ROLES),
    ("POST",    "/api/v1/lobby/1/participants",         Roles.ALL_ROLES),
    ("PUT",     "/api/v1/lobby/1/participants/1",       Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/lobby/1/participants/1",       Roles.ALL_ROLES),
    ("POST",    "/api/v1/lobby/1/connect",              Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/lobby/1/leave",                Roles.ALL_ROLES),
]

LOBBY_VALID_DATA = [
    {"name":    "Lobby Name"},
]

LOBBY_INVALID_DATA = [
    ({"name":   "   "}, "Lobby name cannot be empty"),
    ({},                "Field required"),
]

LOBBY_VALID_UPDATE_DATA = [
    {"name":    "Updated Lobby"},
    {"status":  LobbyStatus.ARCHIVED},
]

LOBBY_INVALID_UPDATE_DATA = [
    ({"name":   "   "}, "Lobby name cannot be empty"),
    ({},                "Lobby update data not provided"),
]

LOBBY_PARTICIPANT_VALID_UPDATE_DATA = [
    {"role":        LobbyParticipantRole.PLAYER}, 
    {"role":        LobbyParticipantRole.SPECTATOR}, 
    {"team_id":     None},
    {"is_active":   False},
    {"is_active":   True},
]

LOBBY_PARTICIPANT_INVALID_UPDATE_DATA = [
    ({},    "Participant update data not provided"),
]

LOBBY_FILTER_DATA = [
    (None,                              LOBBIES_COUNT),
    ({"id":             1},             1),
    ({"name":           "2"},           1),
    ({"name":           "Test Lobby"},  LOBBIES_COUNT),
    ({"host_id":        2},             LOBBIES_COUNT),
    ({"host_id":        1},             0),
    ({"algorithm_id":   1},             LOBBIES_COUNT),
    ({"sort_by":        "id"},          LOBBIES_COUNT),
    ({"sort_order":     "desc"},        LOBBIES_COUNT),
    ({"limit":          2},             2),
    ({"offset":         1},             LOBBIES_COUNT-1),
]

PARTICIPANTS_FILTER_DATA = [
    (None,                                                  PARTICIPANTS_COUNT),
    ({"id":         1},                                     1),
    ({"user_id":    3},                                     1),
    ({"team_id":    1},                                     0),
    ({"role":       LobbyParticipantRole.SPECTATOR.value},  PARTICIPANTS_COUNT),
    ({"sort_by":    "id"},                                  PARTICIPANTS_COUNT),
    ({"sort_order": "desc"},                                PARTICIPANTS_COUNT),
    ({"limit":      2},                                     2),
    ({"offset":     1},                                     PARTICIPANTS_COUNT-1),
]
