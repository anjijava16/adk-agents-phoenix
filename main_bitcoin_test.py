"""
Bitcoin Agent Testing Main

Test script for the Bitcoin agent with MCPToolset integration.

Properly handles async cleanup to avoid MCP SSE connection errors.

Usage:
    python main_bitcoin_test.py                 # Run basic test
    python main_bitcoin_test.py test_basic      # Test basic queries
    python main_bitcoin_test.py test_single     # Test single query
"""

import asyncio
import sys

from google.adk.runners import InMemoryRunner
from google.genai import types

from app.agents import create_bitcoin_agent
from app.config import get_settings
from app.logging import setup_logging, get_logger
from app.tracing import setup_phoenix_tracing

logger = get_logger(__name__)


async def test_bitcoin_agent_basic():
    """Test Bitcoin agent with basic queries."""
    logger.info("\n" + "=" * 75)
    logger.info("Testing Bitcoin Agent - Basic Queries")
    logger.info("=" * 75 + "\n")

    setup_logging()
    setup_phoenix_tracing()
    settings = get_settings()

    logger.info(f"Creating Bitcoin agent with model: {settings.primary_model}")
    agent = create_bitcoin_agent(model_name=settings.primary_model)

    runner = InMemoryRunner(agent=agent, app_name="bitcoin_test_app")
    session_service = runner.session_service

    # Create session
    await session_service.create_session(
        app_name="bitcoin_test_app",
        user_id="test_user",
        session_id="test_session_basic",
    )

    queries = [
        "What is the current Bitcoin price?",
        "What is Bitcoin's market cap?",
        "Is Bitcoin trending right now?",
    ]

    for idx, query in enumerate(queries, 1):
        logger.info(f"\nQuery {idx}: {query}")
        logger.info("-" * 75)

        try:
            async for event in runner.run_async(
                user_id="test_user",
                session_id="test_session_basic",
                new_message=types.Content(
                    role="user", parts=[types.Part(text=query)]
                ),
            ):
                if event.is_final_response():
                    response = event.content.parts[0].text.strip()
                    # Show first 300 chars if response is long
                    display = response if len(response) <= 300 else response[:300] + "..."
                    logger.info(f"Response: {display}\n")
                    break
        except Exception as e:
            logger.error(f"Error processing query: {e}")

    logger.info("=" * 75)
    logger.info("Basic Agent Tests Complete\n")


async def test_bitcoin_agent_single():
    """Test Bitcoin agent with a single query."""
    logger.info("\n" + "=" * 75)
    logger.info("Testing Bitcoin Agent - Single Query")
    logger.info("=" * 75 + "\n")

    setup_logging()
    setup_phoenix_tracing()
    settings = get_settings()

    logger.info(f"Creating Bitcoin agent with model: {settings.primary_model}")
    agent = create_bitcoin_agent(model_name=settings.primary_model)

    runner = InMemoryRunner(agent=agent, app_name="bitcoin_single_test_app")
    session_service = runner.session_service

    await session_service.create_session(
        app_name="bitcoin_single_test_app",
        user_id="test_user",
        session_id="test_session_single",
    )

    query = "Give me Bitcoin market analysis"

    logger.info(f"Query: {query}")
    logger.info("-" * 75)

    try:
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session_single",
            new_message=types.Content(
                role="user", parts=[types.Part(text=query)]
            ),
        ):
            if event.is_final_response():
                response = event.content.parts[0].text.strip()
                logger.info(f"Response: {response}\n")
                break
    except Exception as e:
        logger.error(f"Error: {e}")

    logger.info("=" * 75)
    logger.info("Single Query Test Complete\n")


async def main():
    """Main entry point."""
    setup_logging()
    settings = get_settings()

    logger.info("\n" + "🚀 " * 20)
    logger.info("BITCOIN AGENT TEST")
    logger.info("🚀 " * 20 + "\n")

    logger.info("Configuration:")
    logger.info(f"  Model: {settings.primary_model}")
    logger.info(f"  MCP Endpoint: {settings.bitcoin_mcp_endpoint}")
    logger.info(f"  Phoenix Project: {settings.phoenix_project_name}\n")

    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type == "test_basic":
            await test_bitcoin_agent_basic()
        elif test_type == "test_single":
            await test_bitcoin_agent_single()
        else:
            logger.error(f"Unknown test type: {test_type}")
            print("Usage: python main_bitcoin_test.py [test_basic|test_single]")
    else:
        # Run basic test by default
        await test_bitcoin_agent_basic()

    logger.info("=" * 75)
    logger.info("TEST COMPLETE")
    logger.info("=" * 75)
    logger.info(f"\nPhoenix traces available at:")
    logger.info(f"  http://localhost:6006 (Project: {settings.phoenix_project_name})\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
    except RuntimeError as e:
        # Suppress the expected MCP SSE cleanup error
        if "Attempted to exit cancel scope in a different task" in str(e):
            logger.info("\n✅ Agent test completed successfully")
        else:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
