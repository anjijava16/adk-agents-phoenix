# Bitcoin Agent: MCP Server Integration Guide

## Overview

This guide explains how to configure your existing MCP server with the Bitcoin agent. The Bitcoin tools are currently mocked and ready to connect to your actual MCP server.

## Current State

The Bitcoin tools in `app/tools/bitcoin.py` are mocked implementations that **log "calling MCP server"** but don't actually make requests yet. This is intentional—you control the MCP server connection.

## MCP Server Connection Methods

Choose one based on your MCP server setup:

### Option 1: HTTP-based MCP Server (Recommended for Web APIs)

**When to use:** If your MCP server exposes REST endpoints

**Implementation:**

```python
# app/tools/bitcoin.py
import aiohttp
from app.config import get_settings
from app.logging import get_logger

logger = get_logger(__name__)

async def get_bitcoin_price() -> dict:
    """Fetch Bitcoin price from MCP server via HTTP."""
    settings = get_settings()
    
    headers = {}
    if settings.bitcoin_mcp_api_key:
        headers["Authorization"] = f"Bearer {settings.bitcoin_mcp_api_key}"
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{settings.bitcoin_mcp_endpoint}/api/bitcoin/price"
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Bitcoin price: ${data.get('price')}")
                    return {
                        "status": "success",
                        "price": data.get("price"),
                        "currency": data.get("currency", "USD"),
                        "timestamp": data.get("timestamp")
                    }
                else:
                    logger.error(f"MCP server error: {response.status}")
                    return {
                        "status": "error",
                        "message": f"HTTP {response.status}"
                    }
    except asyncio.TimeoutError:
        logger.error("MCP server request timed out")
        return {
            "status": "error",
            "message": "Request timeout"
        }
    except Exception as e:
        logger.error(f"Error calling MCP server: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


async def get_bitcoin_market_cap() -> dict:
    """Fetch Bitcoin market cap from MCP server."""
    settings = get_settings()
    
    headers = {}
    if settings.bitcoin_mcp_api_key:
        headers["Authorization"] = f"Bearer {settings.bitcoin_mcp_api_key}"
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{settings.bitcoin_mcp_endpoint}/api/bitcoin/market-cap"
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Bitcoin market cap: ${data.get('market_cap_usd')}")
                    return {
                        "status": "success",
                        "market_cap_usd": data.get("market_cap_usd"),
                        "market_cap_btc": data.get("market_cap_btc"),
                        "rank": data.get("rank")
                    }
                else:
                    return {"status": "error", "message": f"HTTP {response.status}"}
    except Exception as e:
        logger.error(f"Error fetching market cap: {e}")
        return {"status": "error", "message": str(e)}


async def get_bitcoin_trend() -> dict:
    """Fetch Bitcoin trend from MCP server."""
    settings = get_settings()
    
    headers = {}
    if settings.bitcoin_mcp_api_key:
        headers["Authorization"] = f"Bearer {settings.bitcoin_mcp_api_key}"
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{settings.bitcoin_mcp_endpoint}/api/bitcoin/trend?days=7"
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Bitcoin trend: {data.get('trend')}")
                    return {
                        "status": "success",
                        "trend": data.get("trend"),
                        "change_percentage": data.get("change_percentage"),
                        "days": 7
                    }
                else:
                    return {"status": "error", "message": f"HTTP {response.status}"}
    except Exception as e:
        logger.error(f"Error fetching trend: {e}")
        return {"status": "error", "message": str(e)}


async def get_bitcoin_analysis() -> dict:
    """Fetch comprehensive Bitcoin analysis from MCP server."""
    settings = get_settings()
    
    headers = {}
    if settings.bitcoin_mcp_api_key:
        headers["Authorization"] = f"Bearer {settings.bitcoin_mcp_api_key}"
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{settings.bitcoin_mcp_endpoint}/api/bitcoin/analysis"
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("Bitcoin analysis fetched")
                    return {
                        "status": "success",
                        "analysis": data
                    }
                else:
                    return {"status": "error", "message": f"HTTP {response.status}"}
    except Exception as e:
        logger.error(f"Error fetching analysis: {e}")
        return {"status": "error", "message": str(e)}
```

**Configuration (.env):**
```bash
BITCOIN_MCP_ENDPOINT=http://localhost:8000
BITCOIN_MCP_API_KEY=your_api_key_here
```

### Option 2: MCP Client Library

**When to use:** If using official MCP Python libraries

**Installation:**
```bash
pip install mcp
```

**Implementation:**

```python
# app/tools/bitcoin.py
import json
from mcp import ClientSession, StdioServerParameters
from app.logging import get_logger

logger = get_logger(__name__)
_mcp_session = None

async def _get_mcp_session():
    """Get or create MCP client session."""
    global _mcp_session
    if _mcp_session is None:
        _mcp_session = ClientSession(
            StdioServerParameters(
                command="python",
                args=["-m", "your_mcp_server_module"]
            )
        )
        await _mcp_session.initialize()
    return _mcp_session

async def get_bitcoin_price() -> dict:
    """Fetch Bitcoin price via MCP client."""
    try:
        session = await _get_mcp_session()
        result = await session.call_tool("get_bitcoin_price", {})
        logger.info(f"Bitcoin price via MCP: ${result.get('price')}")
        return result
    except Exception as e:
        logger.error(f"MCP error: {e}")
        return {"status": "error", "message": str(e)}

# Similar implementations for other tools...
```

### Option 3: Custom MCP Server Class

**When to use:** For tightly integrated server

**Implementation:**

```python
# app/tools/bitcoin.py
from app.mcp_clients import BitcoinMCPClient
from app.logging import get_logger

logger = get_logger(__name__)
bitcoin_client = None

def _get_bitcoin_client():
    """Initialize Bitcoin MCP client."""
    global bitcoin_client
    if bitcoin_client is None:
        bitcoin_client = BitcoinMCPClient(
            endpoint="http://localhost:8000",
            api_key="your_key"
        )
    return bitcoin_client

async def get_bitcoin_price() -> dict:
    """Fetch Bitcoin price from MCP server."""
    try:
        client = _get_bitcoin_client()
        price_data = await client.get_price()
        logger.info(f"Bitcoin price: ${price_data['price']}")
        return {
            "status": "success",
            **price_data
        }
    except Exception as e:
        logger.error(f"MCP client error: {e}")
        return {"status": "error", "message": str(e)}

# Similar for other tools...
```

## Configuration Setup

### Step 1: Update Settings

Add MCP configuration to `app/config/settings.py`:

```python
from dataclasses import dataclass, field
from typing import Optional
from app.config import get_settings

@dataclass
class Settings:
    # ... existing fields ...
    
    # Bitcoin MCP Server Configuration
    bitcoin_mcp_endpoint: str = "http://localhost:8000"
    bitcoin_mcp_api_key: Optional[str] = None
    bitcoin_mcp_timeout: int = 10  # seconds
    bitcoin_mcp_retry_attempts: int = 3
```

### Step 2: Update `.env`

```bash
# Bitcoin MCP Server
BITCOIN_MCP_ENDPOINT=http://localhost:8000
BITCOIN_MCP_API_KEY=your_api_key_here
BITCOIN_MCP_TIMEOUT=10
BITCOIN_MCP_RETRY_ATTEMPTS=3

# Other existing configs...
PHOENIX_PROJECT_NAME=arize_adk
PRIMARY_MODEL=gpt-4o
```

### Step 3: Dependencies

For HTTP integration, ensure you have:

```bash
uv pip install aiohttp
```

Or add to `pyproject.toml`:
```toml
[project]
dependencies = [
    "aiohttp>=3.9.0",
    # ... other deps
]
```

## Testing MCP Connection

### Test 1: Direct MCP Call

```python
# test_bitcoin_mcp.py
import asyncio
from app.tools.bitcoin import (
    get_bitcoin_price,
    get_bitcoin_market_cap,
    get_bitcoin_trend,
    get_bitcoin_analysis
)

async def test_mcp_connection():
    """Test MCP server connection."""
    print("Testing Bitcoin MCP Server Connection...\n")
    
    # Test price
    print("1. Testing get_bitcoin_price()...")
    price_result = await get_bitcoin_price()
    print(f"   Result: {price_result}\n")
    
    # Test market cap
    print("2. Testing get_bitcoin_market_cap()...")
    cap_result = await get_bitcoin_market_cap()
    print(f"   Result: {cap_result}\n")
    
    # Test trend
    print("3. Testing get_bitcoin_trend()...")
    trend_result = await get_bitcoin_trend()
    print(f"   Result: {trend_result}\n")
    
    # Test analysis
    print("4. Testing get_bitcoin_analysis()...")
    analysis_result = await get_bitcoin_analysis()
    print(f"   Result: {analysis_result}\n")
    
    # Summary
    all_success = all([
        price_result.get("status") == "success",
        cap_result.get("status") == "success",
        trend_result.get("status") == "success",
        analysis_result.get("status") == "success"
    ])
    
    if all_success:
        print("✅ All MCP tools working!")
    else:
        print("❌ Some tools failed - check logs")

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
```

Run test:
```bash
uv run test_bitcoin_mcp.py
```

### Test 2: Agent Integration Test

```python
# test_bitcoin_agent_mcp.py
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types
from app.agents import create_bitcoin_agent

async def test_agent_with_mcp():
    """Test Bitcoin agent with MCP server."""
    print("Testing Bitcoin Agent with MCP Server...\n")
    
    agent = create_bitcoin_agent()
    runner = InMemoryRunner(agent=agent, app_name="test_bitcoin")
    
    await runner.session_service.create_session(
        app_name="test_bitcoin",
        user_id="test_user",
        session_id="test_session"
    )
    
    query = "What is the current Bitcoin price and market trend?"
    print(f"Query: {query}\n")
    
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=types.Content(role="user", parts=[types.Part(text=query)])
    ):
        if event.is_final_response():
            print("Agent Response:")
            print(event.content.parts[0].text)
            break

if __name__ == "__main__":
    asyncio.run(test_agent_with_mcp())
```

Run test:
```bash
uv run test_bitcoin_agent_mcp.py
```

## Debugging MCP Issues

### Enable Detailed Logging

```python
# In your agent startup code
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Check MCP Server Health

```bash
# Test if MCP server is running
curl -X GET http://localhost:8000/health

# Test specific endpoint
curl -X GET http://localhost:8000/api/bitcoin/price \
  -H "Authorization: Bearer your_api_key"
```

### Monitor Tool Calls in Logs

```bash
# Watch logs for MCP calls
tail -f app_logs.log | grep -E "MCP|bitcoin|price"
```

## Production Checklist

- [ ] MCP server endpoint configured and tested
- [ ] API key secured in environment (not hardcoded)
- [ ] Timeout values appropriate for your MCP server
- [ ] Error handling covers all failure modes
- [ ] Retry logic for transient failures
- [ ] Phoenix tracing enabled for monitoring
- [ ] Rate limiting considered if needed
- [ ] Caching strategy implemented (if appropriate)
- [ ] All tools return consistent error format
- [ ] Comprehensive logging in place

## Common Issues

### Issue: "Connection refused to MCP server"
**Solution:** Verify endpoint in `.env` and that MCP server is running

### Issue: "Authentication failed"
**Solution:** Check `BITCOIN_MCP_API_KEY` is correct and server supports that auth method

### Issue: "Timeout errors"
**Solution:** Increase `BITCOIN_MCP_TIMEOUT` in settings if MCP server is slow

### Issue: "Tool not found" error from agent
**Solution:** Verify all 4 tool functions are defined in `app/tools/bitcoin.py`

## Ready to Deploy

Once your MCP integration is complete:

```bash
# Verify all tests pass
uv run test_bitcoin_mcp.py
uv run test_bitcoin_agent_mcp.py

# Run example script
uv run examples/bitcoin_agent_example.py

# Check traces in Phoenix
# Navigate to http://localhost:6006 and search for bitcoin_agent events
```

You're ready to integrate the Bitcoin agent into your application!
