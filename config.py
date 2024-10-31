from pydantic_settings import BaseSettings
from decouple import config

class Settings(BaseSettings):

    DB_USER: str = config("DB_USER")
    DB_PASSWORD: str = config("DB_PASSWORD")
    DB_HOST: str = config("DB_HOST")
    DB_NAME: str = config("DB_NAME")

settings = Settings()
