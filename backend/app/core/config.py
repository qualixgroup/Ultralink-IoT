from functools import lru_cache

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ultralink Monitor"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    debug: bool = Field(default=True, validation_alias="APP_DEBUG")

    database_url: str = "postgresql+psycopg://ultralink:ultralink@localhost:5432/ultralink_monitor"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = Field(default="change-me-before-production", min_length=16)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    first_superuser_email: str = "admin@ultralink.io"
    first_superuser_password: str = "admin123"
    first_superuser_name: str = "Ultralink Admin"

    thingsboard_base_url: str = "http://localhost:8080"
    thingsboard_username: str = "tenant@thingsboard.org"
    thingsboard_password: str = "tenant"

    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_username: str | None = None
    mqtt_password: str | None = None

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.app_env != "production":
            return self

        if self.jwt_secret_key == "change-me-before-production" or len(self.jwt_secret_key) < 32:
            raise ValueError("JWT_SECRET_KEY must be unique and at least 32 characters in production")
        if self.first_superuser_password == "admin123":
            raise ValueError("FIRST_SUPERUSER_PASSWORD must be changed in production")
        if "*" in self.cors_origins:
            raise ValueError("CORS_ORIGINS cannot include '*' in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
