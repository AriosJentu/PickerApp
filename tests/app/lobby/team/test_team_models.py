import pytest

from pydantic import ValidationError

from app.schemas.lobby.team import TeamCreate, TeamUpdate


@pytest.mark.parametrize(
    "team_data, is_valid, error_info",
    [
        ({"name": "Team Alpha", "lobby_id": 1}, True,   None),
        ({"name": "   ",        "lobby_id": 1}, False,  "name"),
        ({"name": "",           "lobby_id": 1}, False,  "name"),
    ],
)
def test_team_create_schema(
    team_data: dict[str, str | int], 
    is_valid: bool, 
    error_info: str
):

    if is_valid:
        team = TeamCreate(**team_data)
        assert team.name == team_data["name"].strip()
        assert team.lobby_id == team_data["lobby_id"]
    else:
        with pytest.raises(ValidationError) as exc_info:
            TeamCreate(**team_data)

        assert error_info in str(exc_info.value)


@pytest.mark.parametrize(
    "update_data, is_valid, error_info",
    [
        ({"name": "Updated Team"},  True,  None),
        ({"name": "  "          },  False,  "name"),
        ({"name": ""            },  False,  "name"),
    ],
)
def test_team_update_schema(
    update_data: dict[str, str], 
    is_valid: bool, 
    error_info: str
):

    if is_valid:
        team_update = TeamUpdate(**update_data)
        assert team_update.name == update_data["name"].strip()
    else:
        with pytest.raises(ValidationError) as exc_info:
            TeamUpdate(**update_data)

        assert error_info in str(exc_info.value)
