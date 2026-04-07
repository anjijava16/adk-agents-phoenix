"""Factory for creating LLM model instances."""

from typing import Literal

from google.adk.models.lite_llm import LiteLlm

from app.logging import get_logger

logger = get_logger(__name__)

ModelType = Literal["gpt-4o", "gpt-3.5-turbo", "claude-3-opus", "gemini-pro"]


def create_model(model_name: str) -> LiteLlm:
    """Create an LLM model instance.

    Args:
        model_name: Name of the model to create (e.g., 'gpt-4o', 'claude-3-opus').

    Returns:
        LiteLlm model instance configured for the specified model.

    Raises:
        ValueError: If model_name is not supported.
    """
    supported_models = get_available_models()

    if model_name not in supported_models:
        raise ValueError(
            f"Unsupported model: {model_name}. "
            f"Supported models: {supported_models}"
        )

    logger.info(f"Creating model instance: {model_name}")
    return LiteLlm(model=model_name)


def get_available_models() -> list[str]:
    """Get list of available model names.

    Returns:
        List of supported model identifiers.
    """
    return [
        "gpt-4o",
        "gpt-3.5-turbo",
        "gpt-4-turbo",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "gemini-pro",
        "gemini-1.5-flash",
    ]
