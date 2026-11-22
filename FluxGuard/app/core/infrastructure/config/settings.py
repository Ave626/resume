from pydantic_settings import BaseSettings,SettingsConfigDict
from functools import lru_cache
from pydantic import computed_field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    APP_NAME : str = "FluxGuard"
    ENVIRONMENT : str = "development"
    DEBUG : bool = False

    POSTGRES_HOST : str = "localhost"
    POSTGRES_USER : str = "postgres"
    POSTGRES_PORT : int = 5432
    POSTGRES_PASSWORD : str = "postgres"
    POSTGRES_DB : str = "fluxguard"

    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    RESEND_API_KEY: str | None = None
    EMAIL_FROM: str = "FluxGuard <onboarding@resend.dev>"

    @computed_field
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    REDIS_HOST : str = "localhost"
    REDIS_PORT : int = 6379
    REDIS_DB : int = 0

    @computed_field
    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    RABBITMQ_HOST : str = "localhost"
    RABBITMQ_PORT : int = 5672
    RABBITMQ_USER : str = "guest"
    RABBITMQ_PASSWORD : str = "guest"

    @computed_field
    @property
    def rabbitmq_url(self) -> str:
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

