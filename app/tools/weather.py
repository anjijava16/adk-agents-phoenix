"""Weather tool - retrieves current weather information."""

from app.logging import get_logger

logger = get_logger(__name__)


def get_weather(city: str) -> dict:
    """Retrieve the current weather report for a specified city.

    Args:
        city: The name of the city for which to retrieve the weather report.

    Returns:
        dict: {"status": "success", "report": str} or {"status": "error", "error_message": str}
    """
    logger.info(f"Fetching weather for city: {city}")

    if city.lower() == "new york":
        report = {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
        logger.info(f"Weather report found for {city}")
        return report
    else:
        error_report = {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }
        logger.warning(f"No weather data available for {city}")
        return error_report
