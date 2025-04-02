from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserDataRead(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    external_id: Optional[str] = None
    created_at: datetime


class UserDataCreate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    external_id: Optional[str] = None


class UserDataUpdateSecure(UserDataCreate):
    pass


class UserDataUpdate(UserDataUpdateSecure):
    pass
