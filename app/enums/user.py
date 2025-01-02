from typing import Self
from enum import Enum


class UserRole(int, Enum):
    USER = 1
    MODERATOR = 2
    ADMIN = 3

    def __str__(self):
        return self.name.lower()
    
    def has_access(self, required_role: Self) -> bool:
        return self.value >= required_role.value
