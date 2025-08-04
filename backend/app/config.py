import secrets
import warnings
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",  # Ensure this path is correct relative to where the app runs
        env_ignore_empty=True,
        extra="ignore",
    )
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_V1_STR: str = "/api/v1.0"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    PROJECT_NAME: str
    PROJECT_VERSION: str = "0.1.0"
    PG_HOST: str = "localhost"
    PG_PORT: int = 5432
    PG_USER: str = "user"
    PG_PASSWORD: str = "password"
    PG_DB: str = "database"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.PG_USER,
            password=self.PG_PASSWORD,
            host=self.PG_HOST,
            port=self.PG_PORT,
            path=self.PG_DB,
        )


    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    # Yandex OAuth Configuration
    YANDEX_CLIENT_ID: str = "YOUR_YANDEX_CLIENT_ID"
    YANDEX_CLIENT_SECRET: str = "YOUR_YANDEX_CLIENT_SECRET"
    # This redirect URI must match the one configured in your Yandex App settings
    # and the one used by your frontend to initiate OAuth flow.
    YANDEX_REDIRECT_URI: str = "http://localhost:3000/auth/yandex/callback"

    # MQTT Configuration
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: str = admin
    MQTT_PASSWORD: str = admin
    MQTT_COMMAND_TIMEOUT: float = 30.0
    MQTT_ENABLED: bool = True


    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("PG_PASSWORD", self.PG_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )
        # Optionally, add checks for YANDEX_CLIENT_ID and YANDEX_CLIENT_SECRET
        # if you want to enforce that they are not default values in production.
        # For example:
        # if self.ENVIRONMENT != "local":
        #     self._check_default_secret("YANDEX_CLIENT_ID", self.YANDEX_CLIENT_ID)
        #     self._check_default_secret("YANDEX_CLIENT_SECRET", self.YANDEX_CLIENT_SECRET)

        return self


settings = Settings()  # type: ignore