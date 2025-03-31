from typing import Optional

from pydantic import BaseModel


class UserDataRead(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    external_id: Optional[str] = None


class UserDataCreate(UserDataRead):
    pass


class UserDataUpdate(UserDataCreate):
    pass
