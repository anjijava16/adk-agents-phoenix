"""Bitcoin agent - analyzes Bitcoin market data via MCP server."""

from google.adk.agents import Agent

from app.config import get_settings
from app.logging import get_logger
from app.models import create_model
from google.adk.tools.mcp_tool.mcp_toolset import  MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
    

logger = get_logger(__name__)


def create_bitcoin_agent(model_name: str | None = None) -> Agent:
    """Create and configure a Bitcoin analysis agent.

    This agent uses your Bitcoin MCP server to fetch market data
    and provides analysis and insights about Bitcoin.

    Args:
        model_name: Name of the LLM model to use. 
                   Defaults to PRIMARY_MODEL from settings.

    Returns:
        Configured ADK Agent instance for Bitcoin analysis
    """
    settings = get_settings()

    # Use provided model or fall back to primary model from settings
    if model_name is None:
        model_name = settings.primary_model

    logger.info(f"Creating Bitcoin agent with model '{model_name}'")

    model = create_model(model_name)

    # Initialize MCPToolset with SSE connection to auto-discover tools
    mcp_toolset = MCPToolset(
        connection_params=SseConnectionParams(
            url=settings.bitcoin_mcp_endpoint,
            timeout=settings.bitcoin_mcp_timeout,
        )
    )

    agent = Agent(
        name="bitcoin_agent",
        model=model,
        description="Bitcoin market analyst. Analyzes Bitcoin price, trend, and market metrics.",
        instruction="""You are a Bitcoin market analyst. You help users understand Bitcoin's current market position.

When users ask about Bitcoin:
1. Use available tools to fetch current Bitcoin market data from the MCP server
2. Analyze the data to provide meaningful insights about price, trends, and market cap
3. Explain market implications and answer investment-related questions
4. Be factual and data-driven in your analysis


Use the most appropriate tools to answer the user's question.""",
        tools=[mcp_toolset],  # MCPToolset will auto-discover tools from server
    )

    logger.info("Bitcoin agent created successfully")
    return agent
