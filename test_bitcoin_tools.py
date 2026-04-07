"""
Bitcoin Tools Test Suite

Tests the Bitcoin tools to ensure they work correctly before connecting to MCP server.
"""

import asyncio
import logging
from app.tools.bitcoin import (
    get_bitcoin_price,
    get_bitcoin_market_cap,
    get_bitcoin_trend,
    get_bitcoin_analysis
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_bitcoin_price():
    """Test get_bitcoin_price tool."""
    logger.info("Testing get_bitcoin_price()...")
    result = await get_bitcoin_price()
    assert result["status"] in ["success", "error"], "Invalid status"
    logger.info(f"✅ Result: {result}")
    return result


async def test_bitcoin_market_cap():
    """Test get_bitcoin_market_cap tool."""
    logger.info("Testing get_bitcoin_market_cap()...")
    result = await get_bitcoin_market_cap()
    assert result["status"] in ["success", "error"], "Invalid status"
    logger.info(f"✅ Result: {result}")
    return result


async def test_bitcoin_trend():
    """Test get_bitcoin_trend tool."""
    logger.info("Testing get_bitcoin_trend()...")
    result = await get_bitcoin_trend()
    assert result["status"] in ["success", "error"], "Invalid status"
    logger.info(f"✅ Result: {result}")
    return result


async def test_bitcoin_analysis():
    """Test get_bitcoin_analysis tool."""
    logger.info("Testing get_bitcoin_analysis()...")
    result = await get_bitcoin_analysis()
    assert result["status"] in ["success", "error"], "Invalid status"
    logger.info(f"✅ Result: {result}")
    return result


async def test_all_tools():
    """Run all Bitcoin tool tests."""
    logger.info("\n" + "=" * 75)
    logger.info("Bitcoin Tools Test Suite")
    logger.info("=" * 75)

    try:
        # Run all tests
        results = {
            "get_bitcoin_price": await test_bitcoin_price(),
            "get_bitcoin_market_cap": await test_bitcoin_market_cap(),
            "get_bitcoin_trend": await test_bitcoin_trend(),
            "get_bitcoin_analysis": await test_bitcoin_analysis(),
        }

        # Summary
        logger.info("\n" + "=" * 75)
        logger.info("Test Summary")
        logger.info("=" * 75)

        successful = sum(1 for r in results.values() if r.get("status") == "success")
        total = len(results)

        for tool_name, result in results.items():
            status = "✅" if result.get("status") == "success" else "❌"
            logger.info(f"{status} {tool_name}: {result.get('status')}")

        logger.info(f"\nTotal: {successful}/{total} tools working")

        if successful == total:
            logger.info("\n🎉 All Bitcoin tools are working correctly!")
            logger.info("Next step: Connect to your MCP server")
            logger.info("See MCP_INTEGRATION.md for connection options")
        else:
            logger.warning("\n⚠️  Some tools failed. Check logs for details.")

        return successful == total

    except Exception as e:
        logger.error(f"Test suite failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = asyncio.run(test_all_tools())
    exit(0 if success else 1)
