import random
import string

from passlib.context import CryptContext


class PasswordManager:

    _hasher = CryptContext(schemes=["argon2"], deprecated="auto")


    @classmethod
    def hash(cls, password: str) -> str:
        return cls._hasher.hash(password)


    @classmethod
    def verify(cls, password: str, hashed_password: str) -> bool:
        return cls._hasher.verify(password, hashed_password)


    @classmethod
    def needs_rehash(cls, hashed_password: str) -> bool:
        return cls._hasher.check_needs_rehash(hashed_password)


    @staticmethod
    def generate_secure_password(length: int = 12) -> str:
        
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
