from pydantic import BaseModel


class LogoutResponse(BaseModel):
    detail: str = "Successfully logout"
    