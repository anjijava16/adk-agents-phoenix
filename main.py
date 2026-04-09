import asyncio
from asyncio import events
from time import time

#from google.adk.runners import InMemoryRunner
from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types
import time
from app import create_agent, get_logger, get_settings, setup_logging, setup_phoenix_tracing
from app.services import SQLiteSessionService
from app.services.postgres_session_service import PostgresSessionService

logger = get_logger(__name__)

async def main(query: str, session_id: str):
    setup_logging()
    settings = get_settings()
    setup_phoenix_tracing(console_output=True)

    agent = create_agent(agent_name="test_agent", model_name=settings.primary_model)

    #session_service = SQLiteSessionService()
    session_service = PostgresSessionService()
    artifact_service = InMemoryArtifactService()

    # ✅ Ensure session exists before Runner starts
    existing = await session_service.get_session(
        app_name=settings.app_name,
        user_id=settings.user_id,
        session_id=session_id,
    )
    if existing is None:
        await session_service.create_session(
            app_name=settings.app_name,
            user_id=settings.user_id,
            session_id=session_id,
        )
        logger.info(f"New session started: {session_id}")
    else:
        logger.info(f"Resuming session: {session_id} ({len(existing.events)} prior events)")

    start_time = time.time()

    runner = Runner(
        agent=agent,
        app_name=settings.app_name,
        artifact_service=artifact_service,
        session_service=session_service,
    )

    async for event in runner.run_async(
        user_id=settings.user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user", parts=[types.Part(text=query)]
        ),
    ):
        # ✅ Runner automatically calls append_event — no manual tracking needed
        if event.is_final_response() and event.content:
            elapsed_ms = round((time.time() - start_time) * 1000, 3)
            final_response = event.content.parts[0].text
            print(f"\nAgent: {final_response}")
            print(f"Response time: {elapsed_ms}ms")
        elif event.get_function_calls():
            for fc in event.get_function_calls():
                print(f"Tool call: {fc.name}({fc.args})")
        elif event.get_function_responses():
            for fr in event.get_function_responses():
                print(f"Tool result: {fr.name} → {fr.response}")
if __name__ == "__main__":
    query="What is the weather in New York?"
    session_id ="session_12345"
    asyncio.run(main(query, session_id))
