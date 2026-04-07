"""Legacy entry point - USE main.py INSTEAD.

This file is kept for backwards compatibility.
New code should import from the modular packages instead:

    from app import create_agent, setup_phoenix_tracing, get_settings, get_logger
"""

import asyncio

from google.adk.runners import InMemoryRunner
from google.genai import types

from app import create_agent, get_logger, get_settings, setup_logging, setup_phoenix_tracing

logger = get_logger(__name__)


async def main():
    """Legacy main function - use main.py instead."""
    setup_logging()
    settings = get_settings()
    setup_phoenix_tracing(console_output=True)

    agent = create_agent(agent_name="test_agent", model_name=settings.primary_model)

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
            print(event.content.parts[0].text.strip())


if __name__ == "__main__":
    asyncio.run(main())
