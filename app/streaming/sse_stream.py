"""SSE (Server-Sent Events) streaming utilities for agent responses."""

from typing import AsyncIterator
import json
from datetime import datetime

from app.logging import get_logger

logger = get_logger(__name__)


class SSEStream:
    """Manage Server-Sent Events streaming."""

    def __init__(self, event_type: str = "message"):
        """Initialize SSE stream.

        Args:
            event_type: Type of SSE event (default: "message")
        """
        self.event_type = event_type
        self.created_at = datetime.utcnow().isoformat()

    def format_event(self, data: dict, event_id: int | None = None) -> str:
        """Format data as SSE event.

        Args:
            data: Data to send in the event
            event_id: Optional event ID for client tracking

        Returns:
            Formatted SSE event string
        """
        lines = []

        if event_id is not None:
            lines.append(f"id: {event_id}")

        lines.append(f"event: {self.event_type}")
        lines.append(f"data: {json.dumps(data)}")
        lines.append("")  # Empty line to end event

        return "\n".join(lines)

    async def stream_response(
        self, message: str, metadata: dict | None = None
    ) -> AsyncIterator[str]:
        """Stream a response as SSE events.

        Args:
            message: Response message
            metadata: Optional metadata dict

        Yields:
            Formatted SSE event strings
        """
        logger.info(f"Starting SSE stream for: {message[:50]}...")

        # Send response chunk
        response_data = {
            "type": "response",
            "content": message,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if metadata:
            response_data["metadata"] = metadata

        yield self.format_event(response_data)
        logger.info("SSE response stream completed")

    async def stream_tool_call(self, tool_name: str, result: dict) -> AsyncIterator[str]:
        """Stream a tool call result as SSE events.

        Args:
            tool_name: Name of the tool called
            result: Result from the tool

        Yields:
            Formatted SSE event strings
        """
        logger.info(f"Streaming tool call: {tool_name}")

        tool_data = {
            "type": "tool_result",
            "tool": tool_name,
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
        }

        yield self.format_event(tool_data)
        logger.info(f"Tool call stream completed: {tool_name}")

    def batch_events(self, events: list[dict]) -> str:
        """Combine multiple events into a single SSE block.

        Args:
            events: List of event dicts

        Returns:
            Formatted SSE containing all events
        """
        return "\n".join([self.format_event(event) for event in events])
