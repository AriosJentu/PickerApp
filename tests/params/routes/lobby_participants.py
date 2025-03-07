from app.enums.lobby import LobbyParticipantRole

from tests.constants import PARTICIPANTS_COUNT


PARTICIPANTS_UPDATE_DATA = [
    {"role":        LobbyParticipantRole.PLAYER}, 
    {"team_id":     None},
    {"is_active":   False},
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
