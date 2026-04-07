# ADK Agents Phoenix

Multi-package ADK agent framework with Phoenix tracing and observability.

## Project Structure

```
adk_agents_phoenix/
├── main.py                 # Main entry point
├── pyproject.toml         # Project dependencies
├── README.md              # This file
├── app/
│   ├── __init__.py        # Package exports
│   ├── agents/            # Agent definitions
│   │   ├── __init__.py
│   │   └── base_agent.py  # Agent factory
│   ├── config/            # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py    # Settings and env vars
│   ├── logging/           # Logging utilities
│   │   ├── __init__.py
│   │   └── logger.py      # Logger factory
│   ├── models/            # LLM model configuration
│   │   ├── __init__.py
│   │   └── model_factory.py # Model factory
│   ├── tools/             # Individual tools
│   │   ├── __init__.py
│   │   └── weather.py     # Weather tool
│   ├── tracing/           # Phoenix tracing
│   │   ├── __init__.py
│   │   └── phoenix_tracer.py # Tracing setup
│   ├── utils/             # Utility functions
│   │   └── __init__.py
│   └── adk_agents.py      # Legacy entry point (deprecated)
```

## Key Packages

### `app.config` - Configuration Management
Load settings from environment variables with validation.

```python
from app.config import get_settings

settings = get_settings()
print(settings.primary_model)      # "gpt-4o"
print(settings.phoenix_endpoint)   # "http://127.0.0.1:6006/v1/traces"
```

**Environment Variables:**
- `PRIMARY_MODEL` - Primary LLM model (default: "gpt-4o")
- `FALLBACK_MODEL` - Fallback LLM model (default: "gpt-3.5-turbo")
- `SHIPPING_MODEL` - Shipping model (default: "gpt-4o")
- `PHOENIX_ENDPOINT` - Phoenix collector endpoint (default: "http://127.0.0.1:6006/v1/traces")
- `PHOENIX_ENABLED` - Enable Phoenix tracing (default: "true")
- `PHOENIX_PROJECT_NAME` - Phoenix project name for organization (default: "arize_adk")
- `APP_NAME` - Application name (default: "adk-agents-phoenix")
- `LOG_LEVEL` - Logging level (default: "INFO")

### `app.logging` - Logging
Initialize logging and get logger instances.

```python
from app.logging import setup_logging, get_logger

setup_logging(log_level="DEBUG")
logger = get_logger(__name__)
logger.info("Application started")
```

### `app.tracing` - Phoenix Tracing
Configure OpenTelemetry + Phoenix for distributed tracing with automatic project initialization.

```python
from app.tracing import setup_phoenix_tracing
from app.config import get_settings

settings = get_settings()
print(settings.phoenix_project_name)  # "arize_adk"

tracer_provider = setup_phoenix_tracing(console_output=True)
# All ADK operations are now traced to Phoenix
# Traces appear under project: adk-agents-phoenix in Phoenix UI
```

**Phoenix Project Features:**
- ✅ Project name automatically set from `PHOENIX_PROJECT_NAME` env var
- ✅ Service metadata (name, version) automatically included
- ✅ Traces organized by project in Phoenix dashboard
- ✅ Easy to switch between projects with env var

### `app.models` - Model Configuration
Factory for creating LLM model instances with multiple provider support.

```python
from app.models import create_model, get_available_models

# Create a model instance
model = create_model("gpt-4o")

# List available models
available = get_available_models()
# ["gpt-4o", "gpt-3.5-turbo", "claude-3-opus-20240229", ...]
```

Supported models:
- OpenAI: `gpt-4o`, `gpt-3.5-turbo`, `gpt-4-turbo`
- Anthropic: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`
- Google: `gemini-pro`, `gemini-1.5-flash`

### `app.tools` - Tools
Individual tool modules for agent capabilities.

```python
from app.tools import get_weather

result = get_weather("New York")
# {"status": "success", "report": "..."}
```

**Adding New Tools:**
1. Create a new module: `app/tools/my_tool.py`
2. Define the tool function with docstring
3. Export in `app/tools/__init__.py`
4. Register in agent creation

### `app.agents` - Agent Definitions
Agent factory for creating configured agents.

```python
from app.agents import create_agent

# Create agent with default model
agent = create_agent("my_agent")

# Create agent with specific model
agent = create_agent("my_agent", model_name="claude-3-opus-20240229")
```

## Usage

### Running the Default Application

The `.env` file is automatically loaded when the application starts, so all configuration from `.env` is available immediately.

```bash
# Run with uv (recommended)
uv run main.py
# Loads: PHOENIX_PROJECT_NAME=arize_adk from .env

# Or with python directly (venv must be activated)
python main.py

# Override specific settings via environment variables
PRIMARY_MODEL=claude-3-opus-20240229 python main.py

# Override Phoenix project name
PHOENIX_PROJECT_NAME=custom_project python main.py
```

**Configuration Priority (highest to lowest):**
1. Environment variables (e.g., `PHOENIX_PROJECT_NAME=custom_project`)
2. `.env` file values (e.g., `PHOENIX_PROJECT_NAME=arize_adk`)
3. Hardcoded defaults in code (e.g., `"arize_adk"`)

**Verify Configuration:**
```bash
python verify_phoenix_config.py
# Shows: ✅ All checks passed!
#        Traces will be sent to Phoenix project: arize_adk
```

### Programmatic Usage

```python
import asyncio
from app import create_agent, setup_logging, setup_phoenix_tracing, get_settings
from google.adk.runners import InMemoryRunner
from google.genai import types

async def run_agent():
    setup_logging()
    setup_phoenix_tracing()
    
    settings = get_settings()
    agent = create_agent("my_agent", model_name=settings.primary_model)
    
    runner = InMemoryRunner(agent=agent, app_name="my_app")
    # ... run agent with runner
    
asyncio.run(run_agent())
```

## Adding New Tools

1. **Create tool file** `app/tools/calculator.py`:
```python
from app.logging import get_logger

logger = get_logger(__name__)

def add_numbers(a: float, b: float) -> dict:
    """Add two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        dict with result
    """
    result = a + b
    logger.info(f"Adding {a} + {b} = {result}")
    return {"result": result}
```

2. **Export in** `app/tools/__init__.py`:
```python
from .calculator import add_numbers

__all__ = ["get_weather", "add_numbers"]
```

3. **Register in agent** `app/agents/base_agent.py`:
```python
from app.tools import get_weather, add_numbers

tools=[get_weather, add_numbers]
```

## Adding New Agents

1. **Create agent file** `app/agents/search_agent.py`:
```python
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
        description="Search and information retrieval agent",
        instruction="Use tools to find accurate information",
        tools=[get_weather],  # add more tools as needed
    )
```

2. **Export in** `app/agents/__init__.py`:
```python
from .base_agent import create_agent
from .search_agent import create_search_agent

__all__ = ["create_agent", "create_search_agent"]
```

## Phoenix Tracing Integration

All ADK operations are automatically traced when Phoenix is configured. Traces are organized by project name for easy identification.

```
Phoenix Project: arize_adk
  └── InMemoryRunner.run_async()
      ├── Tool calls (weather, etc.)
      ├── Model invocations
      ├── Agent reasoning
      └── Session management
```

**Project Organization:**
- Project name from `PHOENIX_PROJECT_NAME` env var (default: "arize_adk")
- Service metadata includes app name, version
- All traces automatically include project context
- View traces in Phoenix UI: `http://127.0.0.1:6006`

**Change Project Name:**
```bash
PHOENIX_PROJECT_NAME=my-custom-project python main.py
```

## Testing

Example test structure for new tools:

```python
# tests/tools/test_weather.py
import pytest
from app.tools import get_weather

def test_weather_success():
    result = get_weather("New York")
    assert result["status"] == "success"
    assert "report" in result

def test_weather_not_found():
    result = get_weather("Unknown City")
    assert result["status"] == "error"
    assert "not available" in result["error_message"]
```

## Environment Setup

The `.env` file is automatically loaded on application startup (via `python-dotenv`). Simply edit `.env` with your configuration:

```bash
# .env file - automatically loaded on startup
PRIMARY_MODEL=gpt-4o
FALLBACK_MODEL=gpt-3.5-turbo
PHOENIX_ENDPOINT=http://127.0.0.1:6006/v1/traces
PHOENIX_ENABLED=true
PHOENIX_PROJECT_NAME=arize_adk
LOG_LEVEL=DEBUG
APP_NAME=my-adk-app
```

Then run the application - all values from `.env` are automatically available:

```bash
# With uv (recommended)
uv run main.py

# Or with python
python main.py

# Or manually source if preferred
set -a
source .env
set +a
python main.py
```

**Note:** Environment variables passed at runtime override `.env` values:
```bash
PHOENIX_PROJECT_NAME=my_project python main.py
# Will use my_project instead of arize_adk from .env
```
```

## Debugging

Enable debug logging:
```bash
LOG_LEVEL=DEBUG python main.py
```

Enable console span output:
```python
from app.tracing import setup_phoenix_tracing
setup_phoenix_tracing(console_output=True)  # Prints spans to stdout
```

## Performance Tips

1. **Reuse models**: Models are initialized once via the factory
2. **Session management**: InMemoryRunner persists session state
3. **Async execution**: All I/O operations are async-safe
4. **Tracing overhead**: Phoenix tracing adds ~5-10% overhead in production

## License

Apache-2.0
