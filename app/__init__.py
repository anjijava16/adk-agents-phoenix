"""ADK Agents Phoenix - Multi-package agent framework with Phoenix tracing."""

from app.agents import create_agent, create_bitcoin_agent
from app.config import get_settings
from app.logging import get_logger, setup_logging
from app.tracing import setup_phoenix_tracing

__version__ = "0.1.0"

__all__ = [
    "create_agent",
    "create_bitcoin_agent",
    "get_settings",
    "get_logger",
    "setup_logging",
    "setup_phoenix_tracing",
]
