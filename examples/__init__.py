"""
Examples for extending ADK Agents Phoenix

This directory contains examples of how to:
1. Add new tools
2. Create new agents
3. Use different models
4. Configure tracing
"""

from examples.add_tool_example import calculator_tool_example
from examples.add_agent_example import multi_agent_example
from examples.model_switching_example import model_comparison_example

__all__ = [
    "calculator_tool_example",
    "multi_agent_example", 
    "model_comparison_example",
]
