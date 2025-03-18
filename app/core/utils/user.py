import random
import string

from typing import Optional

from app.modules.auth.user.exceptions import HTTPUserExceptionNoDataProvided


def ensure_user_identifier(
    get_user_id: Optional[int] = None,
    get_username: Optional[str] = None,
    get_email: Optional[str] = None
):
    if not (get_user_id or get_username or get_email):
        raise HTTPUserExceptionNoDataProvided(
            detail="No data provided: 'get_user_id', 'get_username' or 'get_email'"
        )


def generate_random_password(length: int = 12) -> str:

    if length < 8:
        raise ValueError("Password length must be at least 8 characters")

    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+"

    all_characters = lower + upper + digits + symbols

    password = [
        random.choice(lower),
        random.choice(upper),
        random.choice(digits),
        random.choice(symbols),
    ]

    password += random.choices(all_characters, k=length - len(password))
    random.shuffle(password)

    return ''.join(password)
