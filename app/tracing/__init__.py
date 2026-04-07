"""Tracing and observability utilities with Phoenix."""

from .phoenix_tracer import get_tracer_provider, setup_phoenix_tracing

__all__ = ["setup_phoenix_tracing", "get_tracer_provider"]
