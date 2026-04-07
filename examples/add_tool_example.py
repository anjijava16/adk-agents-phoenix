"""
Example: Adding a New Tool

This example shows how to add a calculator tool to the framework.
"""

from app.logging import get_logger

logger = get_logger(__name__)


# Step 1: Define the tool function
def add(a: float, b: float) -> dict:
    """Add two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Dictionary with result
    """
    result = a + b
    logger.info(f"Calculator: {a} + {b} = {result}")
    return {"status": "success", "result": result, "operation": "add"}


def subtract(a: float, b: float) -> dict:
    """Subtract two numbers.
    
    Args:
        a: First number
        b: Second number (subtracted from a)
        
    Returns:
        Dictionary with result
    """
    result = a - b
    logger.info(f"Calculator: {a} - {b} = {result}")
    return {"status": "success", "result": result, "operation": "subtract"}


def multiply(a: float, b: float) -> dict:
    """Multiply two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Dictionary with result
    """
    result = a * b
    logger.info(f"Calculator: {a} * {b} = {result}")
    return {"status": "success", "result": result, "operation": "multiply"}


# Step 2: Export the tools
__all__ = ["add", "subtract", "multiply"]


# Step 3: Create an example function to demonstrate usage
async def calculator_tool_example():
    """Example of using calculator tools with an agent."""
    import asyncio
    from google.adk.agents import Agent
    from google.adk.runners import InMemoryRunner
    from google.genai import types
    from app.models import create_model
    from app.tracing import setup_phoenix_tracing
    from app.logging import setup_logging
    
    setup_logging()
    setup_phoenix_tracing()
    
    # Create agent with calculator tools
    model = create_model("gpt-4o")
    agent = Agent(
        name="calculator_agent",
        model=model,
        description="Agent that performs mathematical calculations",
        instruction="Use the available tools to perform calculations. Always use tools for math operations.",
        tools=[add, subtract, multiply],  # Register the tools
    )
    
    # Run the agent
    runner = InMemoryRunner(agent=agent, app_name="calculator-example")
    session_service = runner.session_service
    
    await session_service.create_session(
        app_name="calculator-example",
        user_id="example_user",
        session_id="example_session"
    )
    
    async for event in runner.run_async(
        user_id="example_user",
        session_id="example_session",
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="What is 42 plus 8?")]
        )
    ):
        if event.is_final_response():
            print(f"Response: {event.content.parts[0].text}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(calculator_tool_example())
