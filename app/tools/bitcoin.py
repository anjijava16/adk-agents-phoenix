"""Bitcoin agent tools using ADK MCPToolset.

MCP Server: https://mcp.api.coingecko.com/sse
Uses MCPToolset from google.adk.tools.mcp_tool for proper integration
"""

from google.adk.tools.mcp_tool import MCPToolset

from app.config import get_settings
from app.logging import get_logger

logger = get_logger(__name__)

# Initialize MCPToolset with CoinGecko MCP server
_mcp_toolset: MCPToolset | None = None


def _get_mcp_toolset() -> MCPToolset:
    """Get or initialize MCPToolset instance.
    
    Returns:
        MCPToolset: Initialized toolset for MCP server
    """
    global _mcp_toolset
    
    if _mcp_toolset is None:
        settings = get_settings()
        logger.info(f"Initializing MCPToolset with endpoint: {settings.bitcoin_mcp_endpoint}")
        
        _mcp_toolset = MCPToolset(
            server_url=settings.bitcoin_mcp_endpoint,
            timeout=settings.bitcoin_mcp_timeout,
            name="bitcoin_mcp",
            description="Bitcoin data from CoinGecko MCP server"
        )
        logger.info("MCPToolset initialized successfully")
    
    return _mcp_toolset


async def get_bitcoin_price() -> dict:
    """Get current Bitcoin price from MCP server.

    Calls the MCP server at https://mcp.api.coingecko.com/sse
    to fetch the current BTC/USD price with change percentage.

    Returns:
        dict: Bitcoin price data from MCP server
    """
    logger.info("Tool: get_bitcoin_price - calling MCP server via MCPToolset")
    try:
        toolset = _get_mcp_toolset()
        result = await toolset.call_tool("get_bitcoin_price", {})
        logger.info(f"Bitcoin price result: {result}")
        return {"status": "success", **result} if result else {"status": "error", "message": "No data returned"}
    except Exception as e:
        logger.error(f"Error in get_bitcoin_price: {e}")
        return {"status": "error", "message": str(e)}


async def get_bitcoin_market_cap() -> dict:
    """Get Bitcoin market cap from MCP server.

    Calls the MCP server at https://mcp.api.coingecko.com/sse
    to fetch current market capitalization and circulating supply.

    Returns:
        dict: Bitcoin market cap data from MCP server
    """
    logger.info("Tool: get_bitcoin_market_cap - calling MCP server via MCPToolset")
    try:
        toolset = _get_mcp_toolset()
        result = await toolset.call_tool("get_bitcoin_market_cap", {})
        logger.info(f"Bitcoin market cap result: {result}")
        return {"status": "success", **result} if result else {"status": "error", "message": "No data returned"}
    except Exception as e:
        logger.error(f"Error in get_bitcoin_market_cap: {e}")
        return {"status": "error", "message": str(e)}


async def get_bitcoin_trend() -> dict:
    """Analyze Bitcoin price trend from MCP server.

    Calls the MCP server at https://mcp.api.coingecko.com/sse
    to fetch 7-day trend analysis (bullish/bearish/neutral).

    Returns:
        dict: Bitcoin trend analysis from MCP server
    """
    logger.info("Tool: get_bitcoin_trend - calling MCP server via MCPToolset")
    try:
        toolset = _get_mcp_toolset()
        result = await toolset.call_tool("get_bitcoin_trend", {"days": 7})
        logger.info(f"Bitcoin trend result: {result}")
        return {"status": "success", **result} if result else {"status": "error", "message": "No data returned"}
    except Exception as e:
        logger.error(f"Error in get_bitcoin_trend: {e}")
        return {"status": "error", "message": str(e)}


async def get_bitcoin_analysis() -> dict:
    """Get comprehensive Bitcoin analysis from MCP server.

    Calls the MCP server at https://mcp.api.coingecko.com/sse
    to fetch aggregated data including price, market cap, and trend.

    Returns:
        dict: Comprehensive Bitcoin analysis from MCP server
    """
    logger.info("Tool: get_bitcoin_analysis - calling MCP server via MCPToolset")
    try:
        toolset = _get_mcp_toolset()
        result = await toolset.call_tool("get_bitcoin_analysis", {})
        logger.info(f"Bitcoin analysis result: {result}")
        return {"status": "success", **result} if result else {"status": "error", "message": "No data returned"}
    except Exception as e:
        logger.error(f"Error in get_bitcoin_analysis: {e}")
        return {"status": "error", "message": str(e)}
