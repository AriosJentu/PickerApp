from typing import Optional, Self

from pydantic import BaseModel, model_validator, field_validator

from app.core.lobby.validators import validate_algorithm, validate_teams_count, validate_name

from app.modules.auth.user.schemas import UserReadRegular


class AlgorithmBase(BaseModel):
    name: str
    description: Optional[str] = None
    algorithm: str
    teams_count: int
    creator_id: int
    

    @field_validator("name")
    def validate_name(cls, name: str):
        return validate_name(name, "Algorithm")
    

    @field_validator("teams_count")
    def validate_teams_count(cls, teams_count: int):
        return validate_teams_count(teams_count)
    

    @model_validator(mode="after")
    def validate_algorithm_data(cls, data: Self):
        algorithm = data.algorithm
        teams_count = data.teams_count

        if teams_count is None or algorithm is None:
            raise ValueError("Both 'teams_count' and 'algorithm' must be provided.")

        validate_algorithm(algorithm, teams_count)
        return data


class AlgorithmCreate(AlgorithmBase):
    pass


class AlgorithmReadSimple(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    algorithm: str
    teams_count: int


class AlgorithmRead(AlgorithmReadSimple):
    creator: UserReadRegular


class AlgorithmUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    algorithm: str
    teams_count: int


    @field_validator("name", mode="before")
    def validate_name(cls, name: Optional[str]):
        return validate_name(name, "Algorithm")
    

    @field_validator("teams_count", mode="before")
    def validate_teams_count(cls, teams_count: Optional[int]):
        return validate_teams_count(teams_count)
    
    
    @model_validator(mode="after")
    def validate_algorithm_data(cls, data: Self):
        algorithm = data.algorithm
        teams_count = data.teams_count

        if teams_count is None or algorithm is None:
            raise ValueError("Both 'teams_count' and 'algorithm' must be provided.")

        validate_algorithm(algorithm, teams_count)
        return data


class AlgorithmResponse(BaseModel):
    id: int
    description: str


class AlgorithmsListCountResponse(BaseModel):
    total_count: int
