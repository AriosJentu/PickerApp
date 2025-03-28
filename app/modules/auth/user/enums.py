from typing import Self
from enum import IntEnum


class UserRole(IntEnum):
    USER = 1
    MODERATOR = 2
    ADMIN = 3

    def __str__(self):
        return self.name.lower()
    
    def has_access(self, required: Self) -> bool:
        return self >= required
