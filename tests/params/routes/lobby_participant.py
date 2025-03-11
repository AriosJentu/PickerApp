from app.enums.lobby import LobbyParticipantRole

from tests.constants import Roles, PARTICIPANTS_COUNT


ROUTES = [
    ("GET",     "/api/v1/lobby/1/participants-count",   Roles.ALL_ROLES),
    ("GET",     "/api/v1/lobby/1/participants",         Roles.ALL_ROLES),
    ("POST",    "/api/v1/lobby/1/participants",         Roles.ALL_ROLES),
    ("PUT",     "/api/v1/lobby/1/participants/1",       Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/lobby/1/participants/1",       Roles.ALL_ROLES),
    ("POST",    "/api/v1/lobby/1/connect",              Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/lobby/1/leave",                Roles.ALL_ROLES),
]

PARTICIPANTS_UPDATE_DATA = [
    {"role":        LobbyParticipantRole.PLAYER}, 
    {"team_id":     None},
    {"is_active":   False},
]

PARTICIPANTS_ALREADY_IN_LOBBY_DATA = [
    (False, 200,    ""),
    (True,  409,    "User already in lobby"),
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
