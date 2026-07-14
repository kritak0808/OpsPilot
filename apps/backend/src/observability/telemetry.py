from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from src.core.config import settings

def initialize_telemetry(app: FastAPI) -> None:
    # Setup standard provider resource
    resource = Resource.create(attributes={
        "service.name": settings.OTEL_SERVICE_NAME,
        "environment": settings.ENV,
    })

    provider = TracerProvider(resource=resource)
    
    # Export telemetry trace maps to console for local testing
    processor = SimpleSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    # Instrument FastAPI requests
    FastAPIInstrumentor.instrument_app(app)
