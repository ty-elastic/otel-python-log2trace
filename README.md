This is an exemplary Python OpenTelemetry app showing manual instrumentation, including reading traces from logs and rehydrating to OTel spans.

# Setup

## Packages

```
pip install -r requirements.txt
```

## .env

Create a local file called `.env` with the following contents

```
# address of elastic APM (or other OTel system)
export OTEL_EXPORTER_OTLP_ENDPOINT=""
# URL encoded, so no spaces allowed in Bearer (replace space with %20, like "Authorization=Bearer%20 abc123")
export OTEL_EXPORTER_OTLP_HEADERS=""
export OTEL_SERVICE_NAME="otel-python-log2trace"
export OTEL_RESOURCE_ATTRIBUTES="service.version=1.0,deployment.environment=dev"
```

# Run

```
source .env
python main.py
```