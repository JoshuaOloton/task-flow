from pydantic_settings import BaseSettings
from decouple import config

class Settings(BaseSettings):

    DB_USER: str = config("DB_USER")
    DB_PASSWORD: str = config("DB_PASSWORD")
    DB_HOST: str = config("DB_HOST")
    DB_NAME: str = config("DB_NAME")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = config("REFRESH_TOKEN_EXPIRE_MINUTES", cast=int)
    ALGORITHM: str = config("ALGORITHM")
    JWT_SECRET_KEY: str = config("JWT_SECRET_KEY")
    JWT_REFRESH_SECRET_KEY: str = config("JWT_REFRESH_SECRET_KEY")
    REDIS_HOST: str = config("REDIS_HOST")
    REDIS_PORT: int = config("REDIS_PORT", cast=int)
    REDIS_SHORT_TTL: int = config("REDIS_SHORT_TTL", cast=int)
    REDIS_MEDIUM_TTL: int = config("REDIS_MEDIUM_TTL", cast=int)

settings = Settings()
