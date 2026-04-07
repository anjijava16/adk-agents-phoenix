# Bitcoin Agent Testing Guide

## Quick Start

Run the complete test suite:

```bash
uv run main_bitcoin_test.py
```

## Individual Tests

Run specific tests:

```bash
# Test only the Bitcoin tools
uv run main_bitcoin_test.py test_tools

# Test basic agent queries
uv run main_bitcoin_test.py test_agent

# Test SSE streaming functionality
uv run main_bitcoin_test.py test_sse

# Test multi-turn conversation
uv run main_bitcoin_test.py test_multiturn
```

## What Gets Tested

### 1. **Tool Testing** (`test_tools`)
- Tests all 4 Bitcoin tools individually
- Calls: `get_bitcoin_price()`, `get_bitcoin_market_cap()`, `get_bitcoin_trend()`, `get_bitcoin_analysis()`
- Verifies MCP server connection
- Shows tool responses

### 2. **Basic Agent Testing** (`test_agent`)
- Creates Bitcoin agent instance
- Runs 3 sample queries:
  - "What is the current Bitcoin price?"
  - "What is Bitcoin's market cap?"
  - "Is Bitcoin trending bullish or bearish right now?"
- Tests agent reasoning and tool usage

### 3. **SSE Streaming Testing** (`test_sse`)
- Tests Server-Sent Events formatting
- Streams query as SSE events
- Streams agent response as SSE events
- Demonstrates real-time streaming capability

### 4. **Multi-turn Conversation Testing** (`test_multiturn`)
- Tests conversation context preservation
- Runs 4-turn conversation:
  1. Price question
  2. Price comparison question
  3. Investment timing question
  4. Risk assessment question
- Verifies agent maintains context

## Test Output

Each test produces:
- ✅ Success indicators
- ❌ Failure indicators  
- Detailed logging of tool calls and responses
- Phoenix tracing information
- Configuration details

## Example Output

```
===============================================================================
Testing Bitcoin Tools
===============================================================================

Testing get_bitcoin_price...
✅ get_bitcoin_price: SUCCESS
   Response: {'status': 'success', 'price': 67500.00, ...}

Testing get_bitcoin_market_cap...
✅ get_bitcoin_market_cap: SUCCESS
   Response: {'status': 'success', 'market_cap_usd': 1417500000000, ...}

...

===============================================================================
Tool Test Summary
===============================================================================
Results: 4/4 tools successful
```

## Monitoring Tests

### View Logs in Real-time

```bash
# In another terminal
tail -f app_logs.log | grep -i bitcoin
```

### Monitor Phoenix Traces

Open http://localhost:6006 and filter for:
- Project: `arize_adk`
- Agent: `bitcoin_agent`

Traces will show:
- Agent creation
- Tool calls
- MCP server responses
- Model reasoning
- Response generation
- Latency metrics

## Configuration

Tests use settings from `.env`:

```bash
# Bitcoin MCP Server
BITCOIN_MCP_ENDPOINT=https://mcp.api.coingecko.com/sse
BITCOIN_MCP_TIMEOUT=30

# Model
PRIMARY_MODEL=gpt-4o

# Phoenix
PHOENIX_PROJECT_NAME=arize_adk
PHOENIX_ENDPOINT=http://127.0.0.1:6006/v1/traces
```

## Troubleshooting

### MCP Server Not Responding

Check the endpoint:
```bash
curl -X GET "https://mcp.api.coingecko.com/sse?tool=get_bitcoin_price"
```

### Tools Test Fails But Agent Works

The MCPToolset in the agent handles errors gracefully. Tools may fail due to:
- Network timeout (increase `BITCOIN_MCP_TIMEOUT`)
- MCP server unavailable (check endpoint URL)
- Tool name mismatch (verify MCP server tool names)

### Agent Takes Too Long

Increase the timeout in `.env`:
```bash
BITCOIN_MCP_TIMEOUT=60
```

### Phoenix Not Showing Traces

Ensure Phoenix is running:
```bash
# Check if Phoenix is running
curl http://localhost:6006

# If not, start Phoenix with Docker
docker run -p 6006:6006 arizeai/phoenix:latest
```

## Test Results Interpretation

| Status | Meaning |
|--------|---------|
| ✅ SUCCESS | Tool/agent working correctly |
| ❌ FAIL | Tool returned error or timeout |
| ⚠️ WARNING | Partial response or degraded service |

## Next Steps After Testing

If all tests pass:

1. ✅ Bitcoin agent is properly configured
2. ✅ MCP server integration is working
3. ✅ SSE streaming is functional
4. ✅ Ready to integrate into your application

## Integration Example

Once tests pass, use the agent in your code:

```python
from app.agents import create_bitcoin_agent
from google.adk.runners import InMemoryRunner
from google.genai import types

agent = create_bitcoin_agent()
runner = InMemoryRunner(agent=agent, app_name="my_app")

# Run agent with user query
async for event in runner.run_async(
    user_id="user123",
    session_id="session123",
    new_message=types.Content(
        role="user",
        parts=[types.Part(text="What is Bitcoin's current price?")]
    )
):
    if event.is_final_response():
        print(event.content.parts[0].text)
```

## Performance Metrics

Expected performance (if MCP server is responsive):

- Tool calls: 1-3 seconds each
- Agent processing: 2-5 seconds per query
- Total response time: 5-10 seconds

## Support

If tests fail:

1. Check MCP server status: `https://mcp.api.coingecko.com/sse`
2. Verify `.env` configuration
3. Check logs: `tail -f app_logs.log`
4. View Phoenix traces: http://localhost:6006
