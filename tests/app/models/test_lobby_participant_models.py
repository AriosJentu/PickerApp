import pytest

from pydantic import ValidationError

from app.modules.lobby.lobby.schemas import LobbyParticipantCreate, LobbyParticipantUpdate
from app.modules.lobby.lobby.enums import LobbyParticipantRole
from tests.utils.types import InputData


@pytest.mark.parametrize(
    "participant_data, is_valid, error_info",
    [
        ({"user_id": 1,     "lobby_id": 1,  "role": LobbyParticipantRole.PLAYER,    "team_id": None},   True,   None),
        ({"user_id": 1,     "lobby_id": 1,  "role": LobbyParticipantRole.SPECTATOR, "team_id": 2},      True,   None),
        ({"user_id": 1,     "lobby_id": 1,  "role": "invalid_role",                 "team_id": 2},      False,  "role"),
    ],
)
def test_lobby_participant_create_schema(
        participant_data: InputData, 
        is_valid: bool, 
        error_info: str
):

    if is_valid:
        participant = LobbyParticipantCreate(**participant_data)
        assert participant.user_id == participant_data["user_id"]
        assert participant.lobby_id == participant_data["lobby_id"]
        assert participant.role == LobbyParticipantRole(participant_data["role"])
        assert participant.team_id == participant_data["team_id"]

    else:
        with pytest.raises(ValidationError) as exc_info:
            LobbyParticipantCreate(**participant_data)

        assert error_info in str(exc_info.value)


@pytest.mark.parametrize(
    "update_data, is_valid, error_info",
    [
        ({"role": LobbyParticipantRole.SPECTATOR,   "team_id": 2},  True,   None),
        ({"role": "invalid_role"                                },  False,  "role"),
    ],
)
def test_lobby_participant_update_schema(
        update_data: InputData, 
        is_valid: bool, 
        error_info: str
):

    if is_valid:
        participant_update = LobbyParticipantUpdate(**update_data)
        assert participant_update.role == (LobbyParticipantRole(update_data["role"]) if "role" in update_data else None)
        assert participant_update.team_id == update_data.get("team_id")
    else:
        with pytest.raises(ValidationError) as exc_info:
            LobbyParticipantUpdate(**update_data)

        assert error_info in str(exc_info.value)
