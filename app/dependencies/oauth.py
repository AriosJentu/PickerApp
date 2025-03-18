from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
def get_oauth2_scheme():
    return oauth2_scheme
