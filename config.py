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

    # Max image size
    max_upload_size_bytes: int = 5 * 1024 * 1024   # 5 MB

    posts_per_page: int = 10

    reset_token_expire_minutes: int = 60

    # Email Configuration Settings
    mail_server: str = "localhost"
    mail_port: int = 587
    mail_username: str = ""
    mail_password: SecretStr = SecretStr("")
    mail_from: str = "noreply@example.com"   # sender address
    mail_use_tls: bool = True

    frontend_url: str = "http://localhost:8000"

    # AWS S3 Configuration
    s3_bucket_name: str
    s3_region: str = "ap-southeast-2"
    s3_access_key_id: SecretStr | None = None
    s3_secret_access_key: SecretStr | None = None
    s3_endpoint_url: str | None = None

settings = Settings()   # Load values from .env file