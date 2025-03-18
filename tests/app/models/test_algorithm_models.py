import pytest

from pydantic import ValidationError

from app.modules.lobby.algorithm.schemas import AlgorithmCreate, AlgorithmUpdate
from tests.types import InputData


@pytest.mark.parametrize(
    "algorithm_data, is_valid, error_info",
    [
        ({"name": "Algo1",          "description": "Test",  "algorithm": "BB PP T",     "teams_count": 2,   "creator_id": 0},   True,   ""),
        ({"name": "Algo1",          "description": "Test",  "algorithm": "BB PP BB T",  "teams_count": 2,   "creator_id": 1},   True,   ""),
        ({"name": "Algo2",          "description": "Test",  "algorithm": "BBB PPP T",   "teams_count": 3,   "creator_id": 2},   True,   ""),
        ({"name": "",               "description": "Test",  "algorithm": "BB P",        "teams_count": 2,   "creator_id": 3},   False,  "Algorithm name cannot be empty"),
        ({"name": "   ",            "description": "Test",  "algorithm": "BB P",        "teams_count": 2,   "creator_id": 3},   False,  "Algorithm name cannot be empty"),
        ({"name": "AlgoInvalid",    "description": "Test",  "algorithm": "BB P",        "teams_count": 2,   "creator_id": 3},   False,  "Size of the step"),
        ({"name": "AlgoInvalid",    "description": "Test",  "algorithm": "",            "teams_count": 2,   "creator_id": 4},   False,  "Algorithm should contain at least one step"),
        ({"name": "AlgoInvalid",    "description": "Test",  "algorithm": "   ",         "teams_count": 2,   "creator_id": 4},   False,  "Algorithm should contain at least one step"),
        ({"name": "AlgoInvalid",    "description": "Test",  "algorithm": "BB PP",       "teams_count": 3,   "creator_id": 5},   False,  "Size of the step"),
        ({"name": "AlgoInvalid",    "description": "Test",  "algorithm": "BB PP T",     "teams_count": 1,   "creator_id": 6},   False,  "Teams count should be in between"),
        ({"name": "AlgoInvalid",    "description": "Test",  "algorithm": "BB PP T",     "teams_count": 0,   "creator_id": 7},   False,  "Teams count should be in between"),
    ]
)
def test_algorithm_create_schema(
        algorithm_data: InputData, 
        is_valid: bool, 
        error_info: str
):
    
    if is_valid:
        algo = AlgorithmCreate(**algorithm_data)
        assert algo.name == algorithm_data["name"]
        assert algo.description == algorithm_data["description"]
        assert algo.algorithm == algorithm_data["algorithm"]
        assert algo.teams_count == algorithm_data["teams_count"]
        assert algo.creator_id == algorithm_data["creator_id"]
    else:
        with pytest.raises(ValidationError) as exception:
            AlgorithmCreate(**algorithm_data)

        assert error_info in str(exception.value)

@pytest.mark.parametrize(
    "update_data, is_valid, error_info",
    [
        ({"name": "NewAlgo",    "algorithm": "BB PP T",     "teams_count": 2}, True,    "algorithm"),
        ({"name": ""                                                        }, False,   "name"),
        ({"name": "    "                                                    }, False,   "name"),
        ({                      "algorithm": "BB P"                         }, False,   "algorithm"),
        ({                                                  "teams_count": 1}, False,   "teams_count"),
        ({                      "algorithm": ""                             }, False,   "algorithm"),
    ]
)
def test_algorithm_update_schema(
        update_data: InputData, 
        is_valid: bool, 
        error_info: str
):

    if is_valid:
        algo_update = AlgorithmUpdate(**update_data)
        for key, value in update_data.items():
            assert getattr(algo_update, key) == value
    else:
        with pytest.raises(ValidationError) as exception:
            AlgorithmUpdate(**update_data)

        assert error_info in str(exception.value)
