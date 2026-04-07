#!/bin/bash
# Bitcoin Agent Quick Reference Guide

## 📋 Quick Start

### View All Components
ls -la app/agents/bitcoin_agent.py
ls -la app/tools/bitcoin.py
ls -la app/streaming/sse_stream.py
ls -la examples/bitcoin_agent_example.py

### Test Bitcoin Tools
uv run test_bitcoin_tools.py

### Run Bitcoin Agent Example
uv run examples/bitcoin_agent_example.py

### Run Batch SSE Example
uv run examples/bitcoin_agent_example.py batch

---

## 🔧 Configuration

### .env Setup
```bash
# Bitcoin MCP Server
BITCOIN_MCP_ENDPOINT=http://localhost:8000
BITCOIN_MCP_API_KEY=your_api_key_here

# Phoenix Configuration
PHOENIX_PROJECT_NAME=arize_adk
PHOENIX_ENDPOINT=http://127.0.0.1:6006/v1/traces

# Model Configuration
PRIMARY_MODEL=gpt-4o
LOG_LEVEL=INFO
```

### Available Models
- gpt-4o (OpenAI) ← Default
- gpt-3.5-turbo (OpenAI)
- claude-3-opus (Anthropic)
- gemini-pro (Google)

---

## 💻 Code Examples

### Create Bitcoin Agent
```python
from app.agents import create_bitcoin_agent

agent = create_bitcoin_agent()
# Uses default model (gpt-4o) from PRIMARY_MODEL env var

# Or specify model
agent = create_bitcoin_agent(model_name="claude-3-opus")
```

### Use SSE Streaming
```python
from app.streaming import SSEStream

sse = SSEStream(event_type="bitcoin_analysis")

# Stream a single event
event = sse.format_event(
    data={"price": 67500, "trend": "bullish"},
    event_id="1"
)
print(event)

# Stream response async
async for sse_event in sse.stream_response("What's Bitcoin price?"):
    print(sse_event)
```

### Call Bitcoin Tools Directly
```python
from app.tools.bitcoin import (
    get_bitcoin_price,
    get_bitcoin_market_cap,
    get_bitcoin_trend,
    get_bitcoin_analysis
)

# Mock implementations for now
result = await get_bitcoin_price()
# {'status': 'success', 'price': 67500.00, ...}
```

### Run Agent with InMemoryRunner
```python
from google.adk.runners import InMemoryRunner
from google.genai import types
from app.agents import create_bitcoin_agent

agent = create_bitcoin_agent()
runner = InMemoryRunner(agent=agent, app_name="bitcoin_app")

async for event in runner.run_async(
    user_id="user123",
    session_id="session123",
    new_message=types.Content(
        role="user",
        parts=[types.Part(text="What is Bitcoin's price?")]
    )
):
    if event.is_final_response():
        print(event.content.parts[0].text)
```

---

## 📁 File Structure

```
Bitcoin Agent Components:
├── app/agents/bitcoin_agent.py       ← Bitcoin agent factory
├── app/tools/bitcoin.py              ← Bitcoin tools (4 functions)
├── app/streaming/sse_stream.py       ← SSE streaming utilities
├── examples/bitcoin_agent_example.py ← Full usage example
├── test_bitcoin_tools.py             ← Tool testing

Documentation:
├── BITCOIN_AGENT.md          ← Complete user guide
├── MCP_INTEGRATION.md        ← MCP integration guide
├── BITCOIN_AGENT_SETUP.md    ← Implementation summary
└── QUICKSTART_BITCOIN.md     ← This file
```

---

## 🔌 MCP Server Integration

### Step 1: Update bitcoin.py with MCP Calls
Edit `app/tools/bitcoin.py` and replace mock implementations:

**From:**
```python
async def get_bitcoin_price() -> dict:
    logger.info("calling MCP server")
    return {"status": "success", "price": 67500.00}
```

**To:**
```python
async def get_bitcoin_price() -> dict:
    url = f"{settings.bitcoin_mcp_endpoint}/api/bitcoin/price"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return {"status": "success", **data}
```

See **MCP_INTEGRATION.md** for 3 different integration options.

### Step 2: Configure .env
```bash
BITCOIN_MCP_ENDPOINT=http://localhost:8000
BITCOIN_MCP_API_KEY=your_api_key
```

### Step 3: Test Connection
```bash
uv run test_bitcoin_tools.py
uv run examples/bitcoin_agent_example.py
```

### Step 4: Monitor in Phoenix
```bash
# Phoenix should be running
open http://localhost:6006
# Check arize_adk project for bitcoin_agent traces
```

---

## 🧪 Testing

### Test Bitcoin Tools
```bash
# Tests all 4 Bitcoin tools
uv run test_bitcoin_tools.py

# Expected output:
# ✅ get_bitcoin_price: success
# ✅ get_bitcoin_market_cap: success
# ✅ get_bitcoin_trend: success
# ✅ get_bitcoin_analysis: success
```

### Test Agent with Example
```bash
# Run streaming example
uv run examples/bitcoin_agent_example.py

# Run batch events example
uv run examples/bitcoin_agent_example.py batch
```

### Manual Tool Test
```python
import asyncio
from app.tools.bitcoin import get_bitcoin_price

result = asyncio.run(get_bitcoin_price())
print(result)
```

---

## 🎯 Bitcoin Agent Features

### Tools Available
1. `get_bitcoin_price()` - Current BTC/USD price
2. `get_bitcoin_market_cap()` - Market cap in USD
3. `get_bitcoin_trend()` - 7-day trend analysis
4. `get_bitcoin_analysis()` - Comprehensive analysis

### Agent Capabilities
- Answers Bitcoin price questions
- Provides market cap information
- Analyzes Bitcoin trends
- Gives investment insights
- Understands market context

### Example Queries
```
"What is Bitcoin's current price?"
→ Uses get_bitcoin_price()

"What's Bitcoin's market cap?"
→ Uses get_bitcoin_market_cap()

"Is Bitcoin bullish or bearish?"
→ Uses get_bitcoin_trend()

"Give me a comprehensive Bitcoin analysis"
→ Uses get_bitcoin_analysis()

"Should I invest in Bitcoin right now?"
→ Uses multiple tools for analysis
```

---

## 📊 SSE Event Format

### Single Event
```
id: 1
event: bitcoin_analysis
data: {"price": 67500, "trend": "bullish"}

```

### Multiple Events (Batch)
```
id: 1
event: bitcoin_analysis
data: {"type": "price", "value": 67500}

id: 2
event: bitcoin_analysis
data: {"type": "trend", "value": "bullish"}

```

### Client-side Reception
```javascript
const eventSource = new EventSource('/bitcoin/stream');
eventSource.addEventListener('bitcoin_analysis', (event) => {
    const data = JSON.parse(event.data);
    console.log('Bitcoin update:', data);
});
```

---

## 🔍 Debugging

### View Agent Tools
```python
from app.agents import create_bitcoin_agent
agent = create_bitcoin_agent()
for tool in agent.tools:
    print(f"Tool: {tool.name} - {tool.description}")
```

### Check Tool Exports
```python
from app.agents import create_bitcoin_agent
from app.tools import get_bitcoin_price, get_bitcoin_market_cap
from app.streaming import SSEStream
print("✅ All exports working")
```

### Monitor Logs
```bash
# Watch for Bitcoin-related logs
tail -f app_logs.log | grep -i bitcoin

# Watch for MCP calls
tail -f app_logs.log | grep -i "calling MCP"

# Watch for Phoenix traces
tail -f app_logs.log | grep -i "phoenix"
```

### Check Phoenix Tracing
```bash
# Open Phoenix UI
open http://localhost:6006

# Search for bitcoin_agent in arize_adk project
# View traces showing:
# - Agent execution
# - Tool calls
# - Model responses
# - Latency information
```

---

## ⚡ Performance Tips

1. **Keep Session Open**
   - Reuse sessions for multiple queries within same conversation

2. **Cache Results**
   - Cache Bitcoin price for 1-5 minutes to reduce MCP calls

3. **Parallel Tool Calls**
   - ADK automatically parallelizes independent tools

4. **Use Streaming**
   - SSE allows showing partial results while processing

5. **Monitor Traces**
   - Use Phoenix to identify slow operations

---

## 🚀 Production Deployment

### Pre-deployment Checklist
- [ ] MCP server endpoint configured
- [ ] API key secured (env variable)
- [ ] All tests passing (`uv run test_bitcoin_tools.py`)
- [ ] Example script runs successfully
- [ ] Phoenix tracing enabled
- [ ] Logging configured appropriately
- [ ] Error handling verified
- [ ] Timeout values appropriate

### Environment Variables Required
```bash
BITCOIN_MCP_ENDPOINT=
BITCOIN_MCP_API_KEY=
PHOENIX_PROJECT_NAME=arize_adk
PHOENIX_ENDPOINT=
PRIMARY_MODEL=gpt-4o
LOG_LEVEL=INFO
```

### Deployment Commands
```bash
# Verify configuration
python verify_phoenix_config.py

# Test all components
uv run test_bitcoin_tools.py
uv run examples/bitcoin_agent_example.py

# Monitor in production
tail -f app_logs.log
open http://localhost:6006  # Phoenix UI
```

---

## 📚 Documentation Links

- **BITCOIN_AGENT.md** - Complete guide with architecture and API
- **MCP_INTEGRATION.md** - 3 options for connecting MCP server
- **BITCOIN_AGENT_SETUP.md** - Implementation summary
- **examples/bitcoin_agent_example.py** - Working code examples

---

## ❓ Common Questions

### Q: Do I need to create an MCP server?
A: No! You already have one. Just integrate it using the steps in MCP_INTEGRATION.md

### Q: What if my MCP server has different endpoints?
A: Update the endpoint URLs in MCP_INTEGRATION.md Section 1 to match your server

### Q: Can I use a different LLM model?
A: Yes! Set PRIMARY_MODEL=claude-3-opus or use create_bitcoin_agent("gemini-pro")

### Q: How do I see the agent working?
A: Run `uv run examples/bitcoin_agent_example.py` and check http://localhost:6006

### Q: What does SSE do?
A: Sends real-time updates to clients using Server-Sent Events (one-way streaming)

### Q: Is the agent working now?
A: Yes! With mock tools. Update bitcoin.py to call your MCP server to see real data.

---

## 🆘 Issues & Solutions

### Agent not using tools
```bash
# Check tools are registered
python -c "from app.agents import create_bitcoin_agent; print(create_bitcoin_agent().tools)"
```

### MCP connection failing
```bash
# Test MCP endpoint
curl http://localhost:8000/health

# Check .env has correct endpoint
grep BITCOIN_MCP_ENDPOINT .env
```

### SSE not formatting correctly
```python
# Each event must end with blank line
event = sse.format_event(data)
# id: 1\nevent: type\ndata: json\n\n
```

### Phoenix not showing traces
```bash
# Verify Phoenix is running
curl http://localhost:6006

# Check PHOENIX_ENDPOINT in .env
grep PHOENIX_ENDPOINT .env
```

---

## 📞 Need Help?

See the full documentation:
- BITCOIN_AGENT.md - Comprehensive guide
- MCP_INTEGRATION.md - Integration options
- examples/bitcoin_agent_example.py - Working examples

Or check logs:
```bash
tail -f app_logs.log
```
