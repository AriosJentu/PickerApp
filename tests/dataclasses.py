
from typing import Generic, TypeVar, Optional
from dataclasses import dataclass

from app.db.base import User

from tests.types import InputData

T = TypeVar("T")

@dataclass
class BaseUserData:
    user: User
    access_token: str
    refresh_token: str
    headers: InputData


@dataclass
class BaseObjectData(Generic[T]):
    id: int
    data: Optional[T]
