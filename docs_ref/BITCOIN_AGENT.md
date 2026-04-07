# Bitcoin Agent Documentation

## Overview

The Bitcoin Agent is an ADK-based agent that analyzes Bitcoin market data using your existing MCP (Model Context Protocol) server. It provides real-time Bitcoin price analysis, market cap monitoring, trend analysis, and comprehensive market insights using SSE (Server-Sent Events) streaming for real-time responses.

## Features

- **Real-time Bitcoin Data**: Fetches current price, market cap, and trend data from your MCP server
- **Market Analysis**: Provides comprehensive Bitcoin market insights
- **SSE Streaming**: Streams responses in real-time using Server-Sent Events
- **Phoenix Tracing**: Full observability with Phoenix/OpenTelemetry integration
- **Multi-model Support**: Works with OpenAI (gpt-4o), Anthropic, and Google models

## Architecture

### Components

1. **Bitcoin Agent** (`app/agents/bitcoin_agent.py`)
   - ADK Agent configured with Bitcoin tools
   - Model: Defaults to `gpt-4o` (configurable via `PRIMARY_MODEL` env var)
   - Name: `bitcoin_agent`

2. **Bitcoin Tools** (`app/tools/bitcoin.py`)
   - `get_bitcoin_price()`: Fetches current BTC/USD price from MCP server
   - `get_bitcoin_market_cap()`: Gets Bitcoin market capitalization
   - `get_bitcoin_trend()`: Analyzes 7-day price trend
   - `get_bitcoin_analysis()`: Comprehensive aggregated analysis

3. **SSE Streaming** (`app/streaming/sse_stream.py`)
   - Real-time event streaming
   - Formats responses as Server-Sent Events
   - Supports response streaming, tool calls, and batch events

## Setup

### 1. Configuration

Ensure your `.env` file has the Bitcoin configuration:

```bash
# Bitcoin MCP Server Connection
BITCOIN_MCP_ENDPOINT=http://localhost:8000  # Your MCP server endpoint
BITCOIN_MCP_API_KEY=your_api_key_here       # If authentication required

# Phoenix Configuration
PHOENIX_PROJECT_NAME=arize_adk
PHOENIX_ENDPOINT=http://127.0.0.1:6006/v1/traces

# Model Configuration (optional, defaults to gpt-4o)
PRIMARY_MODEL=gpt-4o
```

### 2. Connect to Your MCP Server

Edit `app/tools/bitcoin.py` to connect to your MCP server. Replace the mock implementations with actual MCP client calls:

**Current Mock Implementation:**
```python
def get_bitcoin_price() -> dict:
    logger.info("calling MCP server for bitcoin price")
    return {
        "status": "success",
        "price": 67500.00,
        "currency": "USD",
        "timestamp": "2024-01-15T12:30:00Z"
    }
```

**Connect to Your MCP Server (Example):**
```python
import aiohttp
from app.config import get_settings

async def get_bitcoin_price() -> dict:
    settings = get_settings()
    headers = {}
    if settings.bitcoin_mcp_api_key:
        headers["Authorization"] = f"Bearer {settings.bitcoin_mcp_api_key}"
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{settings.bitcoin_mcp_endpoint}/api/bitcoin/price"
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "success",
                        **data
                    }
                else:
                    logger.error(f"MCP server error: {response.status}")
                    return {"status": "error", "message": "Failed to fetch Bitcoin price"}
    except Exception as e:
        logger.error(f"Error calling MCP server: {e}")
        return {"status": "error", "message": str(e)}
```

## Usage

### Basic Usage

```python
from app.agents import create_bitcoin_agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# Create the agent
agent = create_bitcoin_agent()

# Initialize runner
runner = InMemoryRunner(agent=agent, app_name="bitcoin_app")

# Create session
await runner.session_service.create_session(
    app_name="bitcoin_app",
    user_id="user123",
    session_id="session123"
)

# Run query
query = "What is the current Bitcoin price?"
async for event in runner.run_async(
    user_id="user123",
    session_id="session123",
    new_message=types.Content(role="user", parts=[types.Part(text=query)])
):
    if event.is_final_response():
        print(event.content.parts[0].text)
```

### With SSE Streaming

```python
from app.streaming import SSEStream

sse_stream = SSEStream(event_type="bitcoin_analysis")

# Stream the response
async for sse_event in sse_stream.stream_response(
    "What is Bitcoin's current market trend?",
    metadata={"user_id": "user123"}
):
    print(sse_event)  # Send to client via HTTP response
```

### Running the Example

```bash
# Run with streaming responses
uv run examples/bitcoin_agent_example.py

# Run batch SSE events example
uv run examples/bitcoin_agent_example.py batch
```

## API Reference

### Bitcoin Agent Factory

```python
def create_bitcoin_agent(model_name: str | None = None) -> Agent:
    """
    Create a Bitcoin market analysis agent.
    
    Args:
        model_name: Optional model name. Defaults to PRIMARY_MODEL env var.
                   Examples: "gpt-4o", "claude-3-opus", "gemini-pro"
    
    Returns:
        Configured ADK Agent instance with Bitcoin tools
    """
```

### Bitcoin Tools

#### `get_bitcoin_price()` → dict

Returns current Bitcoin price data:

```json
{
  "status": "success",
  "price": 67500.00,
  "currency": "USD",
  "timestamp": "2024-01-15T12:30:00Z"
}
```

#### `get_bitcoin_market_cap()` → dict

Returns Bitcoin market cap data:

```json
{
  "status": "success",
  "market_cap_usd": 1323450000000,
  "market_cap_btc": 20000000,
  "rank": 1
}
```

#### `get_bitcoin_trend()` → dict

Returns 7-day trend analysis:

```json
{
  "status": "success",
  "trend": "bullish",
  "change_percentage": 12.5,
  "days": 7
}
```

#### `get_bitcoin_analysis()` → dict

Returns comprehensive analysis combining all tools:

```json
{
  "status": "success",
  "analysis": {
    "price": 67500.00,
    "market_cap_usd": 1323450000000,
    "trend": "bullish",
    "summary": "Strong bullish momentum in Bitcoin market"
  }
}
```

### SSE Stream API

```python
class SSEStream:
    def __init__(self, event_type: str = "data")
    
    def format_event(self, data: Any, event_id: str | None = None) -> str
        """Format a single SSE event"""
    
    async def stream_response(self, message: str, metadata: dict | None = None)
        """Stream a complete response as SSE events"""
    
    async def stream_tool_call(self, tool_name: str, result: Any)
        """Stream tool call and result as SSE events"""
    
    def batch_events(self, events: list[dict]) -> str
        """Combine multiple events into single SSE block"""
```

## Configuration Variables

Add to `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `BITCOIN_MCP_ENDPOINT` | — | Your Bitcoin MCP server URL |
| `BITCOIN_MCP_API_KEY` | — | API key for MCP server (optional) |
| `PHOENIX_PROJECT_NAME` | `arize_adk` | Phoenix project for tracing |
| `PRIMARY_MODEL` | `gpt-4o` | Default LLM model |
| `LOG_LEVEL` | `INFO` | Logging level |

## Monitoring with Phoenix

Your Bitcoin agent queries are automatically traced in Phoenix. To view:

1. Start Phoenix locally:
   ```bash
   docker run -p 6006:6006 arizeai/phoenix:latest
   ```

2. Open http://localhost:6006

3. Look for traces from `arize_adk` project showing:
   - Agent execution flow
   - Tool calls to MCP server
   - Model responses
   - Latency and error information

## Tool Call Flow

```
User Query
    ↓
Bitcoin Agent (ADK)
    ↓
Tool Selection & Execution
    ├─ get_bitcoin_price() → MCP Server
    ├─ get_bitcoin_market_cap() → MCP Server
    ├─ get_bitcoin_trend() → MCP Server
    └─ get_bitcoin_analysis() → MCP Server
    ↓
Model Reasoning
    ↓
Response Generation
    ↓
SSE Stream → Client
```

## Error Handling

The Bitcoin tools include error handling for MCP server issues:

### Mock Implementation Errors
```python
{
    "status": "error",
    "message": "Failed to fetch Bitcoin price",
    "error_code": "MCP_UNAVAILABLE"
}
```

### Agent Response
The agent will gracefully handle MCP errors and provide context-aware responses based on available data.

## Performance Tips

1. **Cache Results**: Consider caching Bitcoin price data for 1-5 minutes
2. **Parallel Tool Calls**: ADK automatically parallelizes independent tool calls
3. **Streaming**: Use SSE streaming for real-time user feedback
4. **Batch Queries**: Group multiple Bitcoin analyses in single session

## Troubleshooting

### MCP Server Not Responding

Check logs:
```bash
tail -f app_logs.log | grep "calling MCP server"
```

Verify connection:
```bash
curl http://localhost:8000/health
```

### Agent Not Using Tools

Verify tools are registered:
```python
from app.agents import create_bitcoin_agent
agent = create_bitcoin_agent()
print(agent.tools)  # Should show 4 Bitcoin tools
```

### SSE Streaming Issues

Check SSE format in Chrome DevTools:
```
id: 1
event: bitcoin_analysis
data: {"content": "..."}

```

Each event must end with blank line.

## Next Steps

1. **Connect MCP Server**: Update `app/tools/bitcoin.py` with your MCP endpoint
2. **Add Authentication**: Configure `BITCOIN_MCP_API_KEY` if needed
3. **Test Queries**: Run example script and test with sample questions
4. **Monitor Traces**: Check Phoenix UI for agent execution details
5. **Deploy**: Add to your production ADK deployment

## Resources

- [ADK Documentation](https://github.com/google-gemini/google-adk)
- [Phoenix Observability](https://phoenix.arize.com/)
- [Server-Sent Events (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [MCP Protocol](https://modelcontextprotocol.io/)
