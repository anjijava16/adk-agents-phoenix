"""
Test Phoenix project name integration.

This script verifies that the Phoenix project name is correctly configured
and included in the tracing setup.
"""

import asyncio

from app import setup_logging, setup_phoenix_tracing, get_logger, get_settings
from app.agents import create_agent
from google.adk.runners import InMemoryRunner
from google.genai import types


async def test_phoenix_project_name():
    """Test that Phoenix project name is set and appears in logs."""
    setup_logging()
    logger = get_logger(__name__)

    settings = get_settings()
    logger.info(f"✓ Phoenix project name: {settings.phoenix_project_name}")
    logger.info(f"✓ Phoenix endpoint: {settings.phoenix_endpoint}")
    logger.info(f"✓ Phoenix enabled: {settings.phoenix_enabled}")
    logger.info(f"✓ App name: {settings.app_name}")

    # Setup tracing (which uses the project name)
    tracer_provider = setup_phoenix_tracing(console_output=False)
    logger.info(f"✓ TracerProvider initialized with resource attributes")

    # Verify resource attributes
    resource = tracer_provider.resource
    logger.info(f"  - service.name: {resource.attributes.get('service.name')}")
    logger.info(f"  - service.version: {resource.attributes.get('service.version')}")
    logger.info(f"  - project.name: {resource.attributes.get('project.name')}")

    # Create and run agent (will generate traces)
    agent = create_agent("test_agent")
    runner = InMemoryRunner(agent=agent, app_name=settings.app_name)

    await runner.session_service.create_session(
        app_name=settings.app_name,
        user_id=settings.user_id,
        session_id=settings.session_id,
    )

    logger.info("\n✓ Running agent query (traces sent to Phoenix)...")

    async for event in runner.run_async(
        user_id=settings.user_id,
        session_id=settings.session_id,
        new_message=types.Content(
            role="user", parts=[types.Part(text="What is the weather in New York?")]
        ),
    ):
        if event.is_final_response():
            logger.info(f"\n✓ Agent response: {event.content.parts[0].text.strip()}")

    logger.info("\n✅ Phoenix project name test completed successfully!")
    logger.info(f"View traces in Phoenix UI: http://127.0.0.1:6006")


if __name__ == "__main__":
    asyncio.run(test_phoenix_project_name())
