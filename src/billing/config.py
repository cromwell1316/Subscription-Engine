from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for billing engine."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database connection
    DATABASE_URL: str = "sqlite:///./billing.db"

    # Financial defaults
    DEFAULT_CURRENCY: str = "RUB"
    MAX_PAYMENT_RETRIES: int = 3

    # Resilience & Circuit Breaker parameters
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 3
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT_SECONDS: float = 15.0

    # API server settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000


settings = Settings()
