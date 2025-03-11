from tests.constants import ALGORITHMS_COUNT

from tests.constants import Roles


ROUTES = [
    ("POST",    "/api/v1/algorithm/",            Roles.ALL_ROLES),
    ("GET",     "/api/v1/algorithm/list-count",  Roles.ALL_ROLES),
    ("GET",     "/api/v1/algorithm/list",        Roles.ALL_ROLES),
    ("GET",     "/api/v1/algorithm/1",           Roles.ALL_ROLES),
    ("PUT",     "/api/v1/algorithm/1",           Roles.ALL_ROLES),
    ("DELETE",  "/api/v1/algorithm/1",           Roles.ALL_ROLES),
]

ALGORITHM_VALID_DATA = [
    {"name":    "Valid Algorithm 1",    "algorithm":    "BB PP T",      "teams_count": 2},
    {"name":    "Valid Algorithm 1",    "algorithm":    "BP BP T",      "teams_count": 2},
    {"name":    "Valid Algorithm 1",    "algorithm":    "BBB PPP T",    "teams_count": 3},
    {"name":    "Valid Algorithm 1",    "algorithm":    "BPB PBP T",    "teams_count": 3},
]

ALGORITHM_INVALID_DATA = [
    ({"name":   "Invalid Step",         "algorithm":    "MM FS P",      "teams_count": 2},  "Step 'MM' containings incorrect symbols"),
    ({"name":   "Wrong Step Size",      "algorithm":    "BBB PPP T",    "teams_count": 2},  "Size of the step 'BBB' must be equal to teams count"),
    ({"name":   "  ",                   "algorithm":    "BB PP T",      "teams_count": 2},  "Algorithm name cannot be empty"),
    ({"name":   "Missing Algorithm",    "algorithm":    "",             "teams_count": 2},  "Algorithm should contain at least one step"),
    ({"name":   "Negative Teams Count", "algorithm":    "BB PP T",      "teams_count": -1}, "Teams count should be in between"),
]

ALGORITHM_VALID_UPDATE_DATA = [
    {"algorithm":   "BB PP T",          "teams_count":  2},
    {"algorithm":   "BBB PPP T",        "teams_count":  3},
    {"name":        "Valid Algorithm",  "algorithm":    "BBB PPP T",    "teams_count":  3},
]

ALGORITHM_FIELD_REQUIRED = [
    {},
    {"name": "No Algorithm"}, 
    {"algorithm": "BB PP T"}, 
    {"name": "No Teams Count", "algorithm": "BB PP T"}, 
]

ALGORITHM_FILTER_DATA = [
    (None,                                  ALGORITHMS_COUNT),
    ({"id":             1},                 1),
    ({"name":           "2"},               1),
    ({"name":           "Test Algorithm"},  ALGORITHMS_COUNT),
    ({"teams_count":    2},                 ALGORITHMS_COUNT),
    ({"teams_count":    3},                 0),
    ({"sort_by":        "id"},              ALGORITHMS_COUNT),
    ({"sort_order":     "desc"},            ALGORITHMS_COUNT),
    ({"limit":          2},                 2),
    ({"offset":         1},                 ALGORITHMS_COUNT-1),
]
