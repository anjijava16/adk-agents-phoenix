"""Settings and configuration management."""

import os
from dataclasses import dataclass
from pathlib import Path

# Load .env file if it exists
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, continue without loading .env
    pass


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    # Phoenix tracing
    phoenix_endpoint: str = os.getenv(
        "PHOENIX_ENDPOINT", "http://127.0.0.1:6006/v1/traces"
    )
    phoenix_enabled: bool = os.getenv("PHOENIX_ENABLED", "true").lower() == "true"
    phoenix_project_name: str = os.getenv("PHOENIX_PROJECT_NAME", "arize_adk")

    # Model configuration
    shipping_model: str = os.getenv("SHIPPING_MODEL", "gpt-4o")
    primary_model: str = os.getenv("PRIMARY_MODEL", "gpt-4o")
    fallback_model: str = os.getenv("FALLBACK_MODEL", "gpt-3.5-turbo")

    # OpenAI/LiteLLM settings
    litellm_api_key: str | None = os.getenv("LITELLM_API_KEY")

    # MCP Server Configuration
    bitcoin_mcp_endpoint: str = os.getenv(
        "BITCOIN_MCP_ENDPOINT", "https://mcp.api.coingecko.com/sse"
    )
    bitcoin_mcp_timeout: int = int(os.getenv("BITCOIN_MCP_TIMEOUT", "30"))

    # Runner settings
    app_name: str = os.getenv("APP_NAME", "adk-agents-phoenix")
    user_id: str = os.getenv("USER_ID", "default_user")
    session_id: str = os.getenv("SESSION_ID", "default_session")

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    def __post_init__(self) -> None:
        """Validate critical settings."""
        if self.phoenix_enabled and not self.phoenix_endpoint:
            raise ValueError("PHOENIX_ENDPOINT required when Phoenix tracing is enabled")


_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or initialize global settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
