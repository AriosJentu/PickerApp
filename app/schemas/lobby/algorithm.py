from typing import Optional

from pydantic import BaseModel, field_validator, ValidationInfo

from app.core.lobby.validators import validate_algorithm, validate_teams_count

class AlgorithmBase(BaseModel):
    name: str
    description: Optional[str] = None
    algorithm: str
    teams_count: int


    @field_validator("teams_count")
    def validate_teams_count(cls, teams_count):
        return validate_teams_count(teams_count)
    

    @field_validator("algorithm")
    def validate_algorithm(cls, algorithm, info: ValidationInfo):
        return validate_algorithm(algorithm, info.data.get("teams_count"))


class AlgorithmCreate(AlgorithmBase):
    pass


class AlgorithmRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    algorithm: str
    teams_count: int


class AlgorithmUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    algorithm: Optional[str] = None
    teams_count: Optional[int] = None


    @field_validator("teams_count", mode="before")
    def validate_teams_count(cls, teams_count):
        return validate_teams_count(teams_count)
    

    @field_validator("algorithm", mode="before")
    def validate_algorithm(cls, algorithm, info: ValidationInfo):
        return validate_algorithm(algorithm, info.data.get("teams_count"))
