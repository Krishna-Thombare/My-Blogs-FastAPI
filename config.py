from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Load values from .env files automatically
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Database URL
    database_url: str

    # Secret key used for signing JWT access tokens
    secret_key: SecretStr

    # Algorithm used to sign JWT tokens
    algorithm: str = "HS256"

    # Access token in minutes
    access_token_expire_minutes: int = 30

settings = Settings()   # Load values from .env file