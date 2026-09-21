from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class S3Settings(BaseModel):
    endpoint_url: str
    access_key: str
    secret_key: str
    bucket_name: str
    public_url_base: str


class ApiSettings(BaseModel):
    title: str
    debug: bool
    prefix: str


class DatabaseSettings(BaseModel):
    url: str
    echo: bool


class JwtSettings(BaseModel):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = Field(default="development", validation_alias="APP_ENV")
    app_title: str = Field(default="FastAPI Education", validation_alias="APP_TITLE")
    app_debug: bool = Field(default=True, validation_alias="APP_DEBUG")
    api_prefix: str = Field(default="/api", validation_alias="API_PREFIX")
    database_url: str = Field(
        default="sqlite+aiosqlite:///./fastapi_education.db",
        validation_alias="DATABASE_URL",
    )
    database_echo: bool = Field(default=False, validation_alias="DATABASE_ECHO")
    jwt_secret_key: str = Field(validation_alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=30,
        validation_alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    
    redis_url: str = Field(
        default='redis://localhost:6379/0',
        validation_alias='REDIS_URL',
    )
    submission_queue_name: str = Field(
        default='code-submissions',
        validation_alias='SUBMISSION_QUEUE_NAME',
    )
    s3_endpoint_url: str = Field(default="http://localhost:9000", validation_alias="S3_ENDPOINT_URL")
    s3_access_key: str = Field(default="minioadmin", validation_alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(default="minioadmin", validation_alias="S3_SECRET_KEY")
    s3_bucket_name: str = Field(default="course-covers", validation_alias="S3_BUCKET_NAME")

    @property
    def api(self) -> ApiSettings:
        return ApiSettings(
            title=self.app_title,
            debug=self.app_debug,
            prefix=self.api_prefix,
        )

    @property
    def database(self) -> DatabaseSettings:
        return DatabaseSettings(
            url=self.database_url,
            echo=self.database_echo,
        )

    @property
    def jwt(self) -> JwtSettings:
        return JwtSettings(
            secret_key=self.jwt_secret_key,
            algorithm=self.jwt_algorithm,
            access_token_expire_minutes=self.jwt_access_token_expire_minutes,
        )
    
    @property
    def s3(self) -> S3Settings:
        return S3Settings(
            endpoint_url=self.s3_endpoint_url,
            access_key=self.s3_access_key,
            secret_key=self.s3_secret_key,
            bucket_name=self.s3_bucket_name,
            public_url_base=f"{self.s3_endpoint_url.rstrip('/')}/{self.s3_bucket_name}",
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
