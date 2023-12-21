import dateutil.parser
import csv

import otel

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# init opentelemetry
otel.init({"label_to_apply_to_every_trace": "example"})

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("app")

# this is a trivial example of reading audit log lines and generating traces
def log_to_trace(path):

    # pretend we have a csv file formatted like this:
    # start_timestamp, end_timestamp, function_name, result, attribute_key, attribute_value

    # you could do something like this
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for transaction in reader:
            print(transaction)
            serviceName=transaction[0]
            startTimeUnixNano = int(dateutil.parser.parse(transaction[1]).timestamp())*10**9
            endTimeUnixNano = int(dateutil.parser.parse(transaction[2]).timestamp())*10**9
            traceId = transaction[3]
            spanId = transaction[4]
            parentSpanId = transaction[5]
            spanName = transaction[6]
            spanResult = transaction[7]
            spanAttributeKey = transaction[8]
            spanAttributeValue = transaction[9]

            with tracer.start_as_current_span(spanName, start_time=startTimeUnixNano, end_on_exit=False) as span:
                span.set_attribute(spanAttributeKey, spanAttributeValue)
                if spanResult == "OK":
                    span.set_status(Status(StatusCode.OK))
                else:
                    span.set_status(Status(StatusCode.ERROR))
                span.end(endTimeUnixNano)

log_to_trace('data/trace.csv')
