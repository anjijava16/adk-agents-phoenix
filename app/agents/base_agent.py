"""Base agent factory and configuration."""

from google.adk.agents import Agent

from app.config import get_settings
from app.logging import get_logger
from app.models import create_model
from app.tools import get_weather

logger = get_logger(__name__)


def create_agent(agent_name: str = "test_agent", model_name: str | None = None) -> Agent:
    """Create and configure an ADK agent instance.

    Args:
        agent_name: Name for the agent.
        model_name: Name of the LLM model to use. Defaults to PRIMARY_MODEL from settings.

    Returns:
        Configured Agent instance.
    """
    settings = get_settings()

    # Use provided model or fall back to primary model from settings
    if model_name is None:
        model_name = settings.primary_model

    logger.info(f"Creating agent '{agent_name}' with model '{model_name}'")

    model = create_model(model_name)

    agent = Agent(
        name=agent_name,
        model=model,
        description="Agent to answer questions using tools.",
        instruction="You must use the available tools to find an answer.",
        tools=[get_weather],
    )

    logger.info(f"Agent '{agent_name}' created successfully")
    return agent
