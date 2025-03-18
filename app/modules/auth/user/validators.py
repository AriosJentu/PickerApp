import re
from typing import Optional


class UserValidator:
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    @staticmethod
    def username(username: Optional[str]) -> Optional[str]:
        if username is None:
            return None
        
        if len(username) < 3 or not username.strip():
            raise ValueError("Username must be at least 3 characters long.")
        
        return username


    @staticmethod
    def password(password: Optional[str]) -> Optional[str]:
        if password is None:
            return None
        
        if len(password) < 8 or not password.strip():
            raise ValueError("Password must be at least 8 characters long.")
        
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter.")
        
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter.")
        
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit.")
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Password must contain at least one special character.")
        
        return password


    @staticmethod
    def email(email: str) -> str:
        if not email or not email.strip():
            raise ValueError("Email cannot be empty.")

        if not re.match(UserValidator.email_regex, email):
            raise ValueError("Invalid email format.")
        
        return email


    def ensure_user_identifier(
        get_user_id: Optional[int] = None,
        get_username: Optional[str] = None,
        get_email: Optional[str] = None
    ):
        if not (get_user_id or get_username or get_email):
            raise ValueError("No data provided: 'get_user_id', 'get_username' or 'get_email'")
