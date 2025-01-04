from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "PickerApp"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_NAME_TEST: str

    def __get_database_url__(self, dbname: str, engine: str) -> str:
        return  f"postgresql+{engine}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{dbname}"

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return self.__get_database_url__(self.DB_NAME, "psycopg2")
    
    @property
    def DATABASE_URL_ASYNC(self) -> str:
        return self.__get_database_url__(self.DB_NAME, "asyncpg")
    
    @property
    def DATABASE_URL_TEST_SYNC(self) -> str:
        return self.__get_database_url__(self.DB_NAME_TEST, "psycopg2")
    
    @property
    def DATABASE_URL_TEST_ASYNC(self) -> str:
        return self.__get_database_url__(self.DB_NAME_TEST, "asyncpg")

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()
