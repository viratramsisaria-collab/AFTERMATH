from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application
    app_name: str = "AFTERMATH"
    debug: bool = False
    environment: str = "development"

    # AI providers
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-3.5-flash-lite"

    groq_api_key: SecretStr | None = None
    groq_model: str = "openai/gpt-oss-120b"

    otari_api_key: SecretStr | None = None
    otari_base_url: str = "https://api.otari.ai/api/v1"
    otari_model: str = "alibaba/qwen-3.5-35b-a3b"

    # AI routing
    default_ai_provider: str = "gemini"
    ai_timeout: float = Field(default=45.0, gt=0)
    ai_max_retries: int = Field(default=2, ge=0, le=5)
    ai_temperature: float = Field(default=0.4, ge=0, le=2)

    # Database
    database_path: Path = Path("data/aftermath.db")

    # Simulation
    city_seed: int = 42
    simulation_tick_seconds: float = Field(default=1.0, gt=0)
    max_simulation_days: int = Field(default=365, gt=0)

    # World generation
    city_name: str = "NOVA YORK"
    initial_budget: float = Field(default=2_500_000_000, gt=0)

    @property
    def configured_providers(self) -> list[str]:
        providers = []

        if self.gemini_api_key:
            providers.append("gemini")

        if self.groq_api_key:
            providers.append("groq")

        if self.otari_api_key:
            providers.append("otari")

        return providers

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.database_path.as_posix()}"

    def get_api_key(self, provider: str) -> str | None:
        """Retrieve a provider key without exposing it in repr output."""

        attribute = f"{provider.lower()}_api_key"
        secret = getattr(self, attribute, None)

        return secret.get_secret_value() if secret else None

    def ensure_directories(self) -> None:
        """Create application directories when required."""

        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def validate_provider(self, provider: str) -> None:
        """Ensure a provider is configured before use."""

        if provider.lower() not in self.configured_providers:
            raise ValueError(
                f"AI provider '{provider}' is not configured."
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings."""

    return Settings()


settings = get_settings()