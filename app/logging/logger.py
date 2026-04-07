"""Logging configuration and factory."""

import logging
import sys
from typing import Optional

from app.config import get_settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """Configure logging for the application.

    Args:
        log_level: Optional log level (DEBUG, INFO, WARNING, ERROR). Defaults to settings.
    """
    settings = get_settings()
    level = log_level or settings.log_level

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name.

    Args:
        name: Logger name, typically __name__ from the module.

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)
