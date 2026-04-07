# Bitcoin Agent with MCPToolset - Setup & Testing

## Overview

Your Bitcoin agent now uses **MCPToolset** with **SSE (Server-Sent Events)** to connect to your CoinGecko MCP server at `https://mcp.api.coingecko.com/sse`.

## Configuration

### .env Settings

```bash
# Bitcoin MCP Server
BITCOIN_MCP_ENDPOINT=https://mcp.api.coingecko.com/sse
BITCOIN_MCP_TIMEOUT=30

# Model (defaults to gpt-4o)
PRIMARY_MODEL=gpt-4o

# Phoenix Tracing
PHOENIX_PROJECT_NAME=arize_adk
PHOENIX_ENDPOINT=http://127.0.0.1:6006/v1/traces
```

All settings are automatically loaded from `.env`.

## Running Tests

```bash
# Basic test with 3 sample queries
uv run main_bitcoin_test.py

# Or specific tests
uv run main_bitcoin_test.py test_basic    # Multiple queries
uv run main_bitcoin_test.py test_single   # Single query
```

## Understanding the MCP Connection

### How MCPToolset Works

```
Bitcoin Agent
    ↓
MCPToolset (SSE Connection)
    ↓
CoinGecko MCP Server (https://mcp.api.coingecko.com/sse)
    ↓
Auto-discovered tools:
  - get_bitcoin_price
  - get_bitcoin_market_cap
  - get_bitcoin_trend
  - get_bitcoin_analysis
```

### Key Features

✅ **Auto-discovery**: Tools are automatically discovered from the MCP server
✅ **SSE Streaming**: Uses Server-Sent Events for real-time data
✅ **Async/await**: Fully asynchronous for non-blocking execution
✅ **Error handling**: Graceful error handling with fallbacks
✅ **Phoenix tracing**: All operations traced to Phoenix

## Expected Output

```
===============================================================================
BITCOIN AGENT TEST
===============================================================================

Configuration:
  Model: gpt-4o
  MCP Endpoint: https://mcp.api.coingecko.com/sse
  Phoenix Project: arize_adk

===========================================================================
Testing Bitcoin Agent - Basic Queries
===========================================================================

Query 1: What is the current Bitcoin price?
-----------
Response: Bitcoin (BTC) is currently trading at...

Query 2: What is Bitcoin's market cap?
-----------
Response: Bitcoin's current market capitalization is...

===========================================================================
TEST COMPLETE
===========================================================================

Phoenix traces available at:
  http://localhost:6006 (Project: arize_adk)
```

## Common Output Messages

### ✅ Success Message
```
✅ Agent test completed successfully
```
This indicates the agent ran successfully, even if there's a cleanup message below.

### ⚠️ Cleanup Message
```
RuntimeError: Attempted to exit cancel scope in a different task than it was entered in
```

**This is NOT an error - it's a known MCP cleanup message.**

The test script catches and suppresses this message because:
1. The agent has already completed successfully
2. This happens during async cleanup of the MCP SSE connection
3. It's a known issue with how anyio task groups interact with asyncio shutdown
4. It does not affect agent functionality

**The test has still succeeded!**

## Testing Different Models

```bash
# Test with Claude
PRIMARY_MODEL=claude-3-opus uv run main_bitcoin_test.py

# Test with Gemini
PRIMARY_MODEL=gemini-pro uv run main_bitcoin_test.py
```

## Agent Code

The Bitcoin agent is created like this:

```python
from app.agents import create_bitcoin_agent

# Create agent (auto-discovers tools from MCP server)
agent = create_bitcoin_agent()

# Or with specific model
agent = create_bitcoin_agent(model_name="claude-3-opus")
```

**File**: `app/agents/bitcoin_agent.py`

## MCP Server Response Format

The CoinGecko MCP server returns SSE-formatted responses:

```
id: 1
event: data
data: {"status": "success", "price": 67500, "currency": "USD"}

id: 2
event: data
data: {"status": "success", "market_cap_usd": 1417500000000}
```

The MCPToolset automatically parses these SSE events and provides the data to the agent.

## Monitoring Execution

### View Logs

```bash
# In another terminal
tail -f app_logs.log | grep -i bitcoin
```

### Phoenix Tracing

Open http://localhost:6006 and filter for:
- **Project**: `arize_adk`
- **Search**: `bitcoin_agent`

You'll see:
- Agent creation
- Tool calls to MCP
- Model reasoning
- Response generation
- Complete execution trace with latency

## File Structure

```
app/
├── agents/
│   └── bitcoin_agent.py          ← Uses MCPToolset
├── config/
│   └── settings.py               ← Loads Bitcoin MCP config
├── tools/
│   └── bitcoin.py                ← Tool wrappers (optional)
└── ...

main_bitcoin_test.py              ← Test script with proper cleanup
.env                              ← Bitcoin MCP configuration
```

## Troubleshooting

### Agent doesn't respond

1. **Check MCP endpoint**:
   ```bash
   curl -I https://mcp.api.coingecko.com/sse
   ```

2. **Verify .env settings**:
   ```bash
   grep BITCOIN .env
   ```

3. **Check logs**:
   ```bash
   grep -i "bitcoin\|mcp" app_logs.log
   ```

### Timeout errors

Increase timeout in `.env`:
```bash
BITCOIN_MCP_TIMEOUT=60  # Default is 30
```

### Phoenix not showing traces

Ensure Phoenix is running:
```bash
curl http://localhost:6006
# If not running:
docker run -p 6006:6006 arizeai/phoenix:latest
```

## Architecture Diagram

```
┌─────────────────┐
│  User Query     │
└────────┬────────┘
         ↓
┌─────────────────────────────────────┐
│  Bitcoin Agent (ADK)                │
│  - name: bitcoin_agent              │
│  - model: gpt-4o (or specified)     │
└────────┬────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  MCPToolset (SSE Connection)        │
│  - Connects to MCP server via SSE   │
│  - Auto-discovers tools             │
│  - Handles streaming data           │
└────────┬────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  CoinGecko MCP Server               │
│  https://mcp.api.coingecko.com/sse  │
│  - get_bitcoin_price                │
│  - get_bitcoin_market_cap           │
│  - get_bitcoin_trend                │
│  - get_bitcoin_analysis             │
└────────┬────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  LLM (gpt-4o)                       │
│  - Analyzes tool outputs            │
│  - Generates response               │
└────────┬────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  User Response                      │
└─────────────────────────────────────┘

Throughout: Phoenix Tracing captures all operations
```

## Integration Example

Use in your own code:

```python
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types
from app.agents import create_bitcoin_agent
from app.config import get_settings
from app.logging import setup_logging
from app.tracing import setup_phoenix_tracing

async def main():
    setup_logging()
    setup_phoenix_tracing()
    settings = get_settings()
    
    # Create agent - tools auto-discovered from MCP
    agent = create_bitcoin_agent(model_name=settings.primary_model)
    
    # Run with InMemoryRunner
    runner = InMemoryRunner(agent=agent, app_name="my_app")
    
    await runner.session_service.create_session(
        app_name="my_app",
        user_id="user1",
        session_id="session1"
    )
    
    async for event in runner.run_async(
        user_id="user1",
        session_id="session1",
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="What is Bitcoin's current price?")]
        ),
    ):
        if event.is_final_response():
            print(event.content.parts[0].text)
            break

asyncio.run(main())
```

## Next Steps

1. ✅ Run basic test: `uv run main_bitcoin_test.py`
2. ✅ Check Phoenix: http://localhost:6006
3. ✅ Integrate into your application
4. ✅ Monitor traces in production

## Support

- **Documentation**: See `BITCOIN_AGENT.md`
- **Integration guide**: See `MCP_INTEGRATION.md`
- **Test guide**: See `BITCOIN_TEST_GUIDE.md`

---

**Status**: ✅ Bitcoin agent with MCPToolset is ready to use!
