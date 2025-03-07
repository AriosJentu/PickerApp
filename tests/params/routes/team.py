from tests.constants import TEAMS_COUNT


TEAM_DATA_STATUS_ERROR =     [
    ({"name":   "New Team"},    200,    ""),
    ({"name":   "   "},         422,    "Team name cannot be empty"),
    ({},                        422,    "Field required"),
]

TEAM_UPDATE_DATA_STATUS_ERROR =     [
    ({"name":   "Updated Team"},    200,    ""),
    ({"name":   "   "},             422,    "Team name cannot be empty"),
    ({},                            400,    "Team update data not provided"),
]

TEAM_FILTER_DATA = [
    (None,                          TEAMS_COUNT),
    ({"id":         1},             1),
    ({"name":       "2"},           1),
    ({"name":       "Test Team"},   TEAMS_COUNT),
    ({"lobby_id":   1},             TEAMS_COUNT),
    ({"sort_by":    "id"},          TEAMS_COUNT),
    ({"sort_order": "desc"},        TEAMS_COUNT),
    ({"limit":      2},             2),
    ({"offset":     1},             TEAMS_COUNT-1),
]
