"""
QUICK START GUIDE

This guide shows the most common operations to get started with ADK Agents Phoenix.
"""

# 1. BASIC SETUP
# ==============

# Create .env file from example
# cp .env.example .env

# Install dependencies
# pip install -e .

# 2. RUN THE DEFAULT AGENT
# =========================

from app import create_agent, setup_logging, setup_phoenix_tracing, get_settings
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types

async def quick_start():
    setup_logging()
    setup_phoenix_tracing()
    settings = get_settings()
    
    # Create agent
    agent = create_agent("my_agent", model_name=settings.primary_model)
    
    # Run agent
    runner = InMemoryRunner(agent=agent, app_name="quick_start")
    await runner.session_service.create_session(
        app_name="quick_start",
        user_id="user",
        session_id="session"
    )
    
    async for event in runner.run_async(
        user_id="user",
        session_id="session",
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="What is the weather in New York?")]
        )
    ):
        if event.is_final_response():
            print(event.content.parts[0].text)

# asyncio.run(quick_start())


# 3. ADD A NEW TOOL
# =================

# File: app/tools/calculator.py
"""
from app.logging import get_logger

logger = get_logger(__name__)

def add(a: float, b: float) -> dict:
    '''Add two numbers'''
    result = a + b
    logger.info(f"Adding {a} + {b} = {result}")
    return {"status": "success", "result": result}
"""

# Update: app/tools/__init__.py
"""
from .weather import get_weather
from .calculator import add

__all__ = ["get_weather", "add"]
"""

# Update: app/agents/base_agent.py
"""
from app.tools import get_weather, add  # Add this import

def create_agent(agent_name: str = "test_agent", ...):
    ...
    tools=[get_weather, add],  # Add to tools list
"""


# 4. CREATE A NEW AGENT
# =====================

# File: app/agents/search_agent.py
"""
from google.adk.agents import Agent
from app.models import create_model
from app.tools import get_weather

def create_search_agent(model_name: str | None = None) -> Agent:
    if model_name is None:
        from app.config import get_settings
        model_name = get_settings().primary_model
    
    model = create_model(model_name)
    
    return Agent(
        name="search_agent",
        model=model,
        description="Search and information agent",
        instruction="Use tools to find information",
        tools=[get_weather],
    )
"""

# Update: app/agents/__init__.py
"""
from .base_agent import create_agent
from .search_agent import create_search_agent

__all__ = ["create_agent", "create_search_agent"]
"""


# 5. USE DIFFERENT MODELS
# =======================

from app.models import get_available_models, create_model

# List available models
print(get_available_models())
# ['gpt-4o', 'gpt-3.5-turbo', 'gpt-4-turbo', 'claude-3-opus-20240229', ...]

# Create specific model
model = create_model("claude-3-opus-20240229")


# 6. CONFIGURE VIA ENVIRONMENT
# =============================

# Primary model
# PRIMARY_MODEL=gpt-4o

# Fallback model
# FALLBACK_MODEL=gpt-3.5-turbo

# Phoenix tracing endpoint
# PHOENIX_ENDPOINT=http://127.0.0.1:6006/v1/traces

# Phoenix project name (for organizing traces in Phoenix UI)
# PHOENIX_PROJECT_NAME=arize_adk

# Disable Phoenix tracing
# PHOENIX_ENABLED=false

# Change log level
# LOG_LEVEL=DEBUG


# 7. VIEW TRACES
# ==============

# Phoenix UI: http://127.0.0.1:6006

# Or use make command:
# make phoenix-ui


# 8. COMMON MAKE COMMANDS
# ========================

# Run with DEBUG logging
# make dev

# Run with specific model
# make run-model model=gpt-4o

# Run with custom Phoenix endpoint
# make run-endpoint https://my-phoenix:6006/v1/traces

# Run tests
# make test

# Format and lint code
# make format lint


# 9. EXAMPLE FILES
# ================

# See examples/ directory for:
# - examples/add_tool_example.py - How to add new tools
# - examples/add_agent_example.py - How to create multiple agents
# - examples/model_switching_example.py - How to compare models

# Run examples:
# python -m examples.add_tool_example
# python -m examples.add_agent_example
# python -m examples.model_switching_example


# 10. LOGGING
# ===========

from app.logging import get_logger

logger = get_logger(__name__)
logger.info("This is an info message")
logger.debug("Debug details")
logger.warning("Warning message")
logger.error("Error message")

# All logs are structured and include:
# - Timestamp
# - Logger name
# - Log level
# - Message
# - Traceback (for errors)


# 11. NEXT STEPS
# ==============

# 1. Read README.md for full documentation
# 2. Read DESIGN_SPEC.md for architecture details
# 3. Try the examples/ to understand patterns
# 4. Add your own tools in app/tools/
# 5. Create domain-specific agents in app/agents/
# 6. Deploy to Google Cloud (see adk-deploy-guide in skills)
"""
