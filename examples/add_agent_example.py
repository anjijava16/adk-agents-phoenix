"""
Example: Creating Multiple Agents

This example shows how to create different agents for different purposes.
"""

import asyncio

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from app.config import get_settings
from app.logging import setup_logging, get_logger
from app.models import create_model
from app.tools import get_weather
from app.tracing import setup_phoenix_tracing

logger = get_logger(__name__)


def create_weather_agent() -> Agent:
    """Create an agent specialized for weather information."""
    model = create_model("gpt-4o")
    
    return Agent(
        name="weather_agent",
        model=model,
        description="Specialized agent for weather inquiries",
        instruction=(
            "You are a weather expert. Use the available tools to get "
            "weather information. Provide detailed and helpful weather reports."
        ),
        tools=[get_weather],
    )


def create_customer_service_agent() -> Agent:
    """Create an agent for customer service (with tools to be added)."""
    model = create_model("gpt-3.5-turbo")  # Smaller model for cost efficiency
    
    return Agent(
        name="customer_service_agent",
        model=model,
        description="Customer service representative",
        instruction=(
            "You are a helpful customer service representative. "
            "Be polite, professional, and address customer concerns. "
            "Use tools to look up information when needed."
        ),
        tools=[],  # Add customer service tools here (e.g., ticket lookup, FAQ search)
    )


async def run_agent_with_query(agent: Agent, query: str, app_name: str) -> str:
    """Run an agent with a single query and return the response.
    
    Args:
        agent: The agent to run
        query: The user's query
        app_name: Application name for tracing
        
    Returns:
        The agent's response text
    """
    runner = InMemoryRunner(agent=agent, app_name=app_name)
    session_service = runner.session_service
    
    session_id = f"{agent.name}-session"
    await session_service.create_session(
        app_name=app_name,
        user_id="example_user",
        session_id=session_id
    )
    
    response_text = ""
    
    async for event in runner.run_async(
        user_id="example_user",
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=query)]
        )
    ):
        if event.is_final_response():
            response_text = event.content.parts[0].text
    
    return response_text


async def multi_agent_example():
    """Example of running multiple agents with different specializations."""
    setup_logging()
    setup_phoenix_tracing()
    settings = get_settings()
    
    logger.info("Starting multi-agent example")
    
    # Create agents with different purposes
    weather_agent = create_weather_agent()
    customer_service_agent = create_customer_service_agent()
    
    # Run agents with different queries
    print("\n=== Weather Agent ===")
    weather_response = await run_agent_with_query(
        weather_agent,
        "What's the weather in New York?",
        "multi-agent-example"
    )
    print(f"Response: {weather_response}\n")
    
    print("=== Customer Service Agent ===")
    customer_response = await run_agent_with_query(
        customer_service_agent,
        "I have a problem with my order",
        "multi-agent-example"
    )
    print(f"Response: {customer_response}\n")
    
    logger.info("Multi-agent example completed")


if __name__ == "__main__":
    asyncio.run(multi_agent_example())
