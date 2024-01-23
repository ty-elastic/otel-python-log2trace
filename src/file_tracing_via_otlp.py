import requests
import os
import time
import dateutil.parser
import csv

from google.protobuf import json_format

def gen_synthetic_trace(*, serviceName, traceId, spanId, parentSpanId, spanName, startTimeUnixNano, endTimeUnixNano, spanKind, spanAttributes, statusCode):
    return {
      "resourceSpans": [
        {
          "resource": {
            "attributes": [
              {
                "key": "service.name",
                "value": {
                  "stringValue": serviceName
                }
              }
            ]
          },
          "scopeSpans": [
            {
              "scope": {
                "name": "my.library"
              },
              "spans": [
                {
                  "traceId": traceId,
                  "spanId": spanId,
                  "parentSpanId": parentSpanId,
                  "name": spanName,
                  "startTimeUnixNano": startTimeUnixNano,
                  "endTimeUnixNano": endTimeUnixNano,
                  "kind": spanKind,
                  "attributes": spanAttributes,
                  "status": {
                      "code": statusCode
                  }
                }
              ]
            }
          ]
        }
      ]
    }

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

            spanAttributes = [
              {
                "key": spanAttributeKey,
                "value": {
                  "stringValue": spanAttributeValue
                }
              }
            ]

            if spanResult == "OK":
                statusCode = 1
            else:
                statusCode = 2

            trace = gen_synthetic_trace(serviceName=serviceName, traceId=traceId, spanId=spanId, parentSpanId=parentSpanId, 
                                        spanName=spanName, startTimeUnixNano=startTimeUnixNano, endTimeUnixNano=endTimeUnixNano, spanKind=2,
                                        spanAttributes=spanAttributes, statusCode=statusCode)

            r = requests.post(f"{os.getenv('OTEL_EXPORTER_OTLP_HTTP_ENDPOINT')}/v1/traces", json=trace)
            print(r)
            time.sleep(1)

log_to_trace('data/trace.csv')