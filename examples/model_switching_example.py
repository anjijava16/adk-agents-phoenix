"""
Example: Using Different Models

This example shows how to use different LLM models with the same agent.
"""

import asyncio

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from app.config import get_settings
from app.logging import setup_logging, get_logger
from app.models import create_model, get_available_models
from app.tools import get_weather
from app.tracing import setup_phoenix_tracing

logger = get_logger(__name__)


async def run_agent_with_model(model_name: str, query: str) -> str:
    """Run a weather agent with a specific model.
    
    Args:
        model_name: Name of the model to use
        query: User query to run
        
    Returns:
        Agent response
    """
    try:
        model = create_model(model_name)
    except ValueError as e:
        logger.error(f"Model creation failed: {e}")
        return f"Error: {e}"
    
    agent = Agent(
        name=f"agent_{model_name.replace('.', '_')}",
        model=model,
        description=f"Agent running on {model_name}",
        instruction="You are a helpful assistant. Use tools when needed.",
        tools=[get_weather],
    )
    
    runner = InMemoryRunner(agent=agent, app_name="model-comparison")
    session_service = runner.session_service
    
    session_id = f"{model_name}-session"
    await session_service.create_session(
        app_name="model-comparison",
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


async def model_comparison_example():
    """Compare responses from multiple models for the same query."""
    setup_logging()
    setup_phoenix_tracing()
    
    logger.info("Starting model comparison example")
    
    query = "What is the weather in New York? Give a brief response."
    
    # Select models to compare (using models that are likely configured)
    models_to_test = [
        "gpt-4o",
        "gpt-3.5-turbo",
        # Uncomment if configured: "claude-3-opus-20240229",
        # Uncomment if configured: "gemini-pro",
    ]
    
    results = {}
    
    print(f"\nComparing {len(models_to_test)} models with query: '{query}'\n")
    print("=" * 80)
    
    for model_name in models_to_test:
        print(f"\nTesting model: {model_name}")
        print("-" * 40)
        
        try:
            response = await run_agent_with_model(model_name, query)
            results[model_name] = response
            print(f"Response: {response[:200]}...")  # Print first 200 chars
        except Exception as e:
            logger.error(f"Error with model {model_name}: {e}")
            results[model_name] = f"Error: {e}"
            print(f"Error: {e}")
    
    print("\n" + "=" * 80)
    print(f"\nComparison complete. All responses traced to Phoenix.")
    print(f"Available models: {get_available_models()}")
    
    logger.info("Model comparison example completed")


if __name__ == "__main__":
    asyncio.run(model_comparison_example())
