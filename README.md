This is an exemplary Python OpenTelemetry app showing manual instrumentation, including reading traces from logs and rehydrating to OTel spans.

# Setup

* docker desktop

## env vars

Create a local file called `.env` with the following contents

```
# including https://
ELASTIC_APM_SERVER_ENDPOINT=
# just the token
ELASTIC_APM_SERVER_SECRET=
```

# Run

```
docker compose build
docker compose up
```