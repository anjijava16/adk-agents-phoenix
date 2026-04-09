"""Example of using SQLite in-memory session service with ADK agents."""

import asyncio
from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types

from app import create_agent, get_logger, get_settings, setup_logging, setup_phoenix_tracing
from app.services import SQLiteSessionService


logger = get_logger(__name__)


async def main():
    """Main entry point demonstrating SQLite session service."""
    # Initialize components
    setup_logging()
    logger.info("Starting ADK Agents with SQLite In-Memory Session Service")

    settings = get_settings()
    setup_phoenix_tracing(console_output=True)

    # Create agent
    agent = create_agent(agent_name="test_agent", model_name=settings.primary_model)

    # Initialize SQLite in-memory session service
    session_service = SQLiteSessionService()
    artifact_service = InMemoryArtifactService()

    # Create a session
    await session_service.create_session(
        app_name=settings.app_name,
        user_id=settings.user_id,
        session_id=settings.session_id,
        metadata={"source": "example", "version": "1.0"},
    )
    logger.info("✓ Session created with SQLite in-memory backend")

    # Store session values
    await session_service.set_session_value(
        session_id=settings.session_id,
        key="context",
        value={"user_preference": "detailed_answers"},
    )

    # Create runner with SQLite session service
    runner = Runner(
        agent=agent,
        app_name=settings.app_name,
        artifact_service=artifact_service,
        session_service=session_service,
    )

    # Run agent
    logger.info("Running agent with SQLite session service...")
    async for event in runner.run_async(
        user_id=settings.user_id,
        session_id=settings.session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="What is the weather in New York?")],
        ),
    ):
        is_final_response = event.is_final_response()
        if is_final_response:
            response = event.content.parts[0].text
            logger.info(f"Final response: {response}")

    # Retrieve session data
    session_data = await session_service.get_session(
        app_name=settings.app_name,
        user_id=settings.user_id,
        session_id=settings.session_id
    )
    logger.info(f"Session data: {session_data}")

    # List all sessions
    sessions = await session_service.list_sessions(
        app_name=settings.app_name,
        user_id=settings.user_id,
    )
    logger.info(f"Total sessions: {len(sessions)}")

    # Cleanup
    session_service.close()
    logger.info("✓ Session service closed")


if __name__ == "__main__":
    asyncio.run(main())
