import random
import string

from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

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


def get_oauth2_scheme():
    return oauth2_scheme
