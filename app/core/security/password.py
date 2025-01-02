from argon2 import PasswordHasher


ph = PasswordHasher()

def get_password_hash(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, password)
        return True
    except:
        return False
