import pytest

from pydantic import ValidationError

from app.schemas.lobby.lobby import LobbyCreate, LobbyUpdate
from app.enums.lobby import LobbyStatus


@pytest.mark.parametrize(
    "lobby_data, is_valid, error_info",
    [
        ({"name": "Test Lobby",     "description": "A cool lobby",  "host_id": 1,   "algorithm_id": 1},     True,   None),
        ({"name": "",               "description": "No name",       "host_id": 1,   "algorithm_id": 1},     False,  "name"),
        ({"name": "   ",            "description": "No name",       "host_id": 1,   "algorithm_id": 1},     False,  "name"),
        ({"name": "Valid",          "description": "No host",                       "algorithm_id": 1},     False,  "host_id"),
        ({"name": "Valid",          "description": "No algorithm",  "host_id": 1                     },     False,  "algorithm_id"),
    ],
)
def test_lobby_create_schema_valid(
        lobby_data: dict[str, str | int], 
        is_valid: bool, 
        error_info: str
):

    if is_valid:
        lobby = LobbyCreate(**lobby_data)
        assert lobby.name == lobby_data["name"]
        assert lobby.description == lobby_data.get("description")
        assert lobby.host_id == lobby_data["host_id"]
        assert lobby.algorithm_id == lobby_data["algorithm_id"]
    else:
        with pytest.raises(ValidationError) as exc_info:
            LobbyCreate(**lobby_data)

        assert error_info in str(exc_info.value)


@pytest.mark.parametrize(
    "update_data, is_valid, error_info",
    [
        ({"name": "New Name",   "description": "Updated description",   "host_id": 2,   "algorithm_id": 2   },  True,   None),
        ({                                                              "host_id": None                     },  True,   None),
        ({                                                                              "algorithm_id": None},  True,   None),
        ({"name": ""                                                                                        },  False,  "name"),
        ({"name": "   "                                                                                     },  False,  "name"),
    ],
)
def test_lobby_update_schema_valid(
        update_data: dict[str, str | int], 
        is_valid: bool, 
        error_info: str
):
    
    if is_valid:
        lobby_update = LobbyUpdate(**update_data)
        assert lobby_update.name == update_data.get("name")
        assert lobby_update.description == update_data.get("description")
        assert lobby_update.host_id == update_data.get("host_id")
        assert lobby_update.algorithm_id == update_data.get("algorithm_id")
    else:
        with pytest.raises(ValidationError) as exc_info:
            LobbyUpdate(**update_data)

        assert error_info in str(exc_info.value)


@pytest.mark.parametrize(
    "status, is_valid",
    [
        (LobbyStatus.ACTIVE,    True),
        (LobbyStatus.ARCHIVED,  True),
        ("invalid_status",      False),
    ],
)
def test_lobby_status_enum(
        status: LobbyStatus, 
        is_valid: bool
):
    
    if is_valid:
        assert LobbyStatus(status).value == status.value
    else:
        with pytest.raises(ValueError):
            LobbyStatus(status)
