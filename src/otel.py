
# for HTTP1.1
# from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
# from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
# for HTTP2
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry import trace
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
)
from opentelemetry.instrumentation.logging import LoggingInstrumentor

from opentelemetry.sdk.metrics import (
    Counter,
    Histogram,
    MeterProvider,
    ObservableCounter,
    ObservableGauge,
    ObservableUpDownCounter,
    UpDownCounter,
)
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    PeriodicExportingMetricReader,
)

# this will auto-inject traceid/spanid into log lines
def init_otel_logging():
    LoggingInstrumentor().instrument(set_logging_format=True)

def init_otel_tracing(resources):
    provider = TracerProvider(resource=Resource.create(resources))
    processor = BatchSpanProcessor(OTLPSpanExporter())
    provider.add_span_processor(processor)
    # sets the global default tracer provider
    trace.set_tracer_provider(provider)

    # setup auto-instrumentation for requests
    instrumentor = RequestsInstrumentor()
    instrumentor.instrument()

def init_otel_metrics(resources):

    temporality = {
        Counter: AggregationTemporality.CUMULATIVE,
        UpDownCounter: AggregationTemporality.CUMULATIVE,
        Histogram: AggregationTemporality.CUMULATIVE,
        ObservableCounter: AggregationTemporality.CUMULATIVE,
        ObservableUpDownCounter: AggregationTemporality.CUMULATIVE,
        ObservableGauge: AggregationTemporality.CUMULATIVE,
    }

    metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(preferred_temporality=temporality))
    provider = MeterProvider(shutdown_on_exit=True, metric_readers=[metric_reader], resource=Resource.create(attributes=resources))
    # sets the global default metrics provider
    metrics.set_meter_provider(provider)

def init(resources):
    init_otel_logging()
    init_otel_tracing(resources)
    init_otel_metrics(resources)