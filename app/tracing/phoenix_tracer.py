"""Phoenix tracing setup and configuration."""

from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from app.config import get_settings
from app.logging import get_logger

logger = get_logger(__name__)

_tracer_provider: trace_sdk.TracerProvider | None = None


def setup_phoenix_tracing(console_output: bool = True) -> trace_sdk.TracerProvider:
    """Initialize and configure Phoenix tracing with OpenTelemetry.

    Args:
        console_output: If True, also print spans to console for debugging.

    Returns:
        Configured TracerProvider instance.
    """
    global _tracer_provider

    settings = get_settings()

    if not settings.phoenix_enabled:
        logger.warning("Phoenix tracing is disabled (PHOENIX_ENABLED=false)")
        _tracer_provider = trace_sdk.TracerProvider()
        return _tracer_provider

    logger.info(
        f"Setting up Phoenix tracing to {settings.phoenix_endpoint} "
        f"(project: {settings.phoenix_project_name})"
    )

    # Create resource with project and service metadata
    resource = Resource.create(
        {
            "service.name": settings.app_name,
            "service.version": "0.1.0",
            "project.name": settings.phoenix_project_name,
        }
    )

    _tracer_provider = trace_sdk.TracerProvider(resource=resource)

    # Add OTLP exporter for Phoenix
    otlp_exporter = OTLPSpanExporter(endpoint=settings.phoenix_endpoint)
    _tracer_provider.add_span_processor(SimpleSpanProcessor(otlp_exporter))

    # Optionally add console exporter for debugging
    if console_output:
        console_exporter = ConsoleSpanExporter()
        _tracer_provider.add_span_processor(SimpleSpanProcessor(console_exporter))
        logger.info("Console span exporter enabled")

    # Instrument Google ADK
    GoogleADKInstrumentor().instrument(tracer_provider=_tracer_provider)
    logger.info("Google ADK instrumentation enabled")

    return _tracer_provider


def get_tracer_provider() -> trace_sdk.TracerProvider:
    """Get the global tracer provider instance.

    Returns:
        TracerProvider instance. Creates one if not already initialized.
    """
    global _tracer_provider

    if _tracer_provider is None:
        _tracer_provider = setup_phoenix_tracing()

    return _tracer_provider
