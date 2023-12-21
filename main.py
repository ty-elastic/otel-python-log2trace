import logging
import requests
import random
import dateutil.parser
import csv

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

# this is a trivial example of reading audit log lines and generating traces
def log_to_trace(path):

    # pretend we have a csv file formatted like this:
    # start_timestamp, end_timestamp, function_name, result, attribute_key, attribute_value

    # you could do something like this
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for transaction in reader:
            print(transaction)
            start_timestamp = int(dateutil.parser.parse(transaction[0]).timestamp())*10**9
            end_timestamp = int(dateutil.parser.parse(transaction[1]).timestamp())*10**9
            function_name = transaction[2]
            result = transaction[3]
            attribute_key = transaction[4]
            attribute_value = transaction[5]

            with tracer.start_as_current_span(function_name, start_time=start_timestamp, end_on_exit=False) as span:
                span.set_attribute(attribute_key, attribute_value)
                if result == "OK":
                    span.set_status(Status(StatusCode.OK))
                else:
                    span.set_status(Status(StatusCode.ERROR))
                span.end(end_timestamp)


log_to_trace('trace.csv')

# test traditional spans
# for x in range(0, 10):
#     do_work()
#     time.sleep(1)



