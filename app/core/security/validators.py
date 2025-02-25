import re
from typing import Optional


def validate_username(username: Optional[str]) -> Optional[str]:
    if username is None:
        return None
    
    if len(username) < 3 or not username.strip():
        raise ValueError("Username must be at least 3 characters long.")
    
    return username


def validate_password(password: Optional[str]) -> Optional[str]:
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


def validate_email(email: str) -> str:
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not email or not email.strip():
        raise ValueError("Email cannot be empty.")

    if not re.match(email_regex, email):
        raise ValueError("Invalid email format.")
    
    return email
