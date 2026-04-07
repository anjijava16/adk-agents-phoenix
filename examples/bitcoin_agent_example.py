"""
Example: Bitcoin Agent with MCP Server and SSE Streaming

This example demonstrates:
1. Creating a Bitcoin agent that uses your MCP server
2. Running queries with the agent
3. Streaming responses using SSE (Server-Sent Events)
"""

import asyncio
import json

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from app.agents import create_bitcoin_agent
from app.config import get_settings
from app.logging import setup_logging, get_logger
from app.streaming import SSEStream
from app.tracing import setup_phoenix_tracing

logger = get_logger(__name__)


async def run_bitcoin_agent_with_sse():
    """Run Bitcoin agent with SSE streaming example."""
    setup_logging()
    setup_phoenix_tracing()
    settings = get_settings()

    logger.info("Starting Bitcoin Agent with SSE Streaming")

    # Create the Bitcoin agent (uses your MCP server)
    agent = create_bitcoin_agent(model_name=settings.primary_model)

    # Initialize runner
    runner = InMemoryRunner(agent=agent, app_name="bitcoin_agent_app")
    session_service = runner.session_service

    await session_service.create_session(
        app_name="bitcoin_agent_app",
        user_id="bitcoin_user",
        session_id="bitcoin_session",
    )

    # Initialize SSE stream
    sse_stream = SSEStream(event_type="bitcoin_analysis")

    # Bitcoin analysis queries
    queries = [
        "What is the current Bitcoin price and what does the trend look like?",
        "Give me a comprehensive Bitcoin market analysis including market cap and volume.",
        "Is Bitcoin bullish or bearish right now based on the 7-day trend?",
    ]

    for idx, query in enumerate(queries, 1):
        print(f"\n{'=' * 75}")
        print(f"Query {idx}: {query}")
        print("=" * 75)

        # Stream the query
        async for event_str in sse_stream.stream_response(
            query, metadata={"query_number": idx}
        ):
            print(event_str)
            print()

        # Run agent with the query
        logger.info(f"Processing query: {query}")

        async for event in runner.run_async(
            user_id="bitcoin_user",
            session_id="bitcoin_session",
            new_message=types.Content(role="user", parts=[types.Part(text=query)]),
        ):
            if event.is_final_response():
                response = event.content.parts[0].text.strip()
                logger.info(f"Agent response: {response[:100]}...")

                # Stream the response using SSE
                result_data = {
                    "response": response,
                    "agent": "bitcoin_agent",
                    "query": query,
                }

                async for sse_event_str in sse_stream.stream_tool_call(
                    "bitcoin_analysis", result_data
                ):
                    print(sse_event_str)
                    print()

                # Print the response
                print("\nAgent Response:")
                print(response)

    logger.info("Bitcoin agent SSE streaming example completed")


async def run_bitcoin_agent_batch():
    """Run Bitcoin agent with batch SSE events."""
    setup_logging()
    setup_phoenix_tracing()
    settings = get_settings()

    logger.info("Starting Bitcoin Agent with Batch SSE Events")

    agent = create_bitcoin_agent(model_name=settings.primary_model)
    runner = InMemoryRunner(agent=agent, app_name="bitcoin_batch_app")
    session_service = runner.session_service

    await session_service.create_session(
        app_name="bitcoin_batch_app",
        user_id="bitcoin_user",
        session_id="bitcoin_batch_session",
    )

    sse_stream = SSEStream(event_type="bitcoin_batch")

    query = "Analyze Bitcoin's current market position and give me investment insights."

    logger.info(f"Running batch query: {query}")

    async for event in runner.run_async(
        user_id="bitcoin_user",
        session_id="bitcoin_batch_session",
        new_message=types.Content(role="user", parts=[types.Part(text=query)]),
    ):
        if event.is_final_response():
            response = event.content.parts[0].text.strip()

            # Batch multiple events into single SSE block
            events = [
                {
                    "type": "agent_analysis",
                    "content": response,
                    "source": "bitcoin_agent",
                    "model": settings.primary_model,
                },
                {
                    "type": "metadata",
                    "query": query,
                    "status": "completed",
                },
            ]

            print("\nBatch SSE Events:")
            batch_sse = sse_stream.batch_events(events)
            print(batch_sse)
            print()

            print("\nAgent Analysis:")
            print(response)

    logger.info("Batch SSE example completed")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        asyncio.run(run_bitcoin_agent_batch())
    else:
        asyncio.run(run_bitcoin_agent_with_sse())
