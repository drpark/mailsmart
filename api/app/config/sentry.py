import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    # Variables Sentry
    sentry_dsn: str | None = Field(default=None, alias="SENTRY_DSN")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_prefix="",
        extra='allow'  # Permet les variables supplémentaires dans le .env
    )


def init_sentry():
    """
    Initialise Sentry si un DSN est configuré,
    sinon continue sans monitoring Sentry
    """
    try:
        settings = Settings()

        if not settings.sentry_dsn:
            print(
                "Warning: Sentry DSN not configured. Running without Sentry monitoring.")
            return

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            integrations=[
                FastApiIntegration(
                    transaction_style="endpoint"
                )
            ]
        )
        print(f"Sentry initialized in {settings.environment} mode")
    except Exception as e:
        print(f"Failed to initialize Sentry: {str(e)}")
        print("Running without Sentry monitoring.")


def capture_exception(error: Exception, context: dict = None):
    """Capture une exception si Sentry est initialisé"""
    if not sentry_sdk.Hub.current.client:
        print(f"Error (not sent to Sentry): {str(error)}")
        if context:
            print(f"Context: {context}")
        return

    if context:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_exception(error)
    else:
        sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", context: dict = None):
    """Capture un message si Sentry est initialisé"""
    if not sentry_sdk.Hub.current.client:
        print(f"{level.upper()}: {message}")
        if context:
            print(f"Context: {context}")
        return

    if context:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_message(message, level=level)
    else:
        sentry_sdk.capture_message(message, level=level)
