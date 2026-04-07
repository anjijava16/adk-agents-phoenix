import asyncio

from google.adk.runners import InMemoryRunner
from google.genai import types

from app import create_skills_agent, get_logger, get_settings, setup_logging, setup_phoenix_tracing

logger = get_logger(__name__)


async def main():
    """Main entry point for ADK agents with Phoenix tracing."""
    # Initialize all components
    setup_logging()
    logger.info("Starting ADK Agents Phoenix application")

    settings = get_settings()
    logger.info(f"✓ Phoenix project name: {settings.phoenix_project_name}")
    logger.info(f"✓ Phoenix endpoint: {settings.phoenix_endpoint}")
    
    setup_phoenix_tracing(console_output=True)

    # Create agent with primary model
    agent = create_skills_agent(model_name=settings.primary_model)

    # Run agent
    logger.info(f"Running agent with app_name={settings.app_name}")
    runner = InMemoryRunner(agent=agent, app_name=settings.app_name)
    session_service = runner.session_service

    await session_service.create_session(
        app_name=settings.app_name,
        user_id=settings.user_id,
        session_id=settings.session_id,
    )

    async for event in runner.run_async(
        user_id=settings.user_id,
        session_id=settings.session_id,
        new_message=types.Content(
            role="user", parts=[types.Part(text="What is the weather in New York?")]
        ),
    ):
        if event.is_final_response():
            response = event.content.parts[0].text.strip()
            logger.info(f"Agent response: {response}")
            print(response)

    logger.info("Agent execution completed")


if __name__ == "__main__":
    asyncio.run(main())
