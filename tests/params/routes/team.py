from tests.constants import Roles, TEAMS_COUNT


ROUTES = [
    ("POST",    "/api/v1/teams/",            Roles.ALL_ROLES),
    ("GET",     "/api/v1/teams/list-count",  Roles.ALL_ROLES),
    ("GET",     "/api/v1/teams/list",        Roles.ALL_ROLES),
    ("GET",     "/api/v1/teams/1",           Roles.ALL_ROLES),
    ("PUT",     "/api/v1/teams/1",           Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/teams/1",           Roles.ALL_ROLES),
]

TEAM_VALID_DATA = [
    {"name":    "New Team"},
]

TEAM_INVALID_DATA = [
    ({"name":   "   "}, "Team name cannot be empty"),
    ({},                "Field required"),
]

TEAM_UPDATE_INVALID_DATA = [
    ({"name":   "   "}, "Team name cannot be empty"),
    ({},                "Team update data not provided"),
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
