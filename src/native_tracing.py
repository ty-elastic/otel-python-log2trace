import logging
import requests
import random
import time

import otel

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry import metrics

# init opentelemetry
otel.init({"label_to_apply_to_every_trace": "example"})

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("app")

# create a meter from the global metric provider
meter = metrics.get_meter("app")
# create a counter metric
work_counter = meter.create_counter(
    "work_counter", unit="1", description="Count of work"
)
# and a histogram metric
requests_size = meter.create_histogram(
        name="request_size_bytes",
        description="size of requests",
        unit="byte"
    )

# this is an example of a function which can be auto-instrumented through annotation
# this annotation will automatically create a span called do_more_work
@tracer.start_as_current_span("do_more_work")
def do_more_work():
    print("doing some work...")

def do_work():
    # this creates a new span - everything under the 'with' will be part of this span
    with tracer.start_as_current_span("parent") as parent:
        # increment counter metric
        work_counter.add(1, attributes={"work.type": "test"})

        # set some attributes
        parent.set_attribute("operation.value", 1)
        parent.set_attribute("operation.name", "Saying hello!")
        parent.set_attribute("operation.other-stuff", [1, 2, 3])

        # generate a log message tagged with traceid/spanid
        logging.getLogger().info("This is a log message")

        # Create a nested span to track nested work
        with tracer.start_as_current_span("child") as child:
            # create an event on this child span
            child.add_event("getting forecast")
            # record size metric
            requests_size.record(random.randint(0, 100), {"url": "https://geocoding-api.open-meteo.com/v1/forecast"})
            try:
                # make a call to a remote REST service, with auto-instrumented requests
                requests.get("https://geocoding-api.open-meteo.com/v1/forecast")
            except Exception as ex:
                child.set_status(Status(StatusCode.ERROR))
                # record exception
                child.record_exception(ex)
            # call into child function which is instrumented
            do_more_work()


while True:
    do_work()
    time.sleep(1)



