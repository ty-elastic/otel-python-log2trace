import requests
import os
import time
import dateutil.parser
import csv

from google.protobuf import json_format

def gen_synthetic_metric(*, serviceName, timestamp, gaugeMetrics, traceId = None, spanId = None, metricAttributes = None):
  generatedMetrics = {
    "resourceMetrics": [
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
        "scopeMetrics": [
          {
            # "scope": {
            #   "attributes": []
            # },
            "metrics": []
          }
        ]
      }
    ]
  }

#   for metricAttribute in metricAttributes:
#      generatedMetrics['resourceMetrics'][0]['scopeMetrics'][0]['scope']['attributes'].append(
#         {
#             "key": metricAttribute,
#             "value": {
#               "stringValue": metricAttributes[metricAttribute]
#             } 
#         }
#      )

  for guageMetric in gaugeMetrics:
    generatedMetric = {}
    generatedMetric['name'] = guageMetric
    generatedMetric['unit'] = "1"
    generatedMetric['gauge'] = {}

    generatedMetric['gauge']['dataPoints'] = [      
        {
          "asDouble": gaugeMetrics[guageMetric],
          "timeUnixNano": timestamp,
          "attributes": []
        }
      ]
    for metricAttribute in metricAttributes:
      generatedMetric['gauge']['dataPoints'][0]['attributes'].append(
        {
            "key": metricAttribute,
            "value": {
              "stringValue": metricAttributes[metricAttribute]
            } 
        }
      )

    if traceId != None and spanId != None:
      generatedMetric['gauge']['dataPoints'][0]['attributes'].append(
        {
            "key": 'traceId',
            "value": {
              "stringValue": traceId
            } 
        }
      )
      generatedMetric['gauge']['dataPoints'][0]['attributes'].append(
        {
            "key": 'spanId',
            "value": {
              "stringValue": spanId
            } 
        }
      )

    # if traceId != None and spanId != None:
    # generatedMetric['gauge']['dataPoints'][0]['exemplars'] = []
    # exemplar = {}
    # exemplar['asDouble'] = gaugeMetrics[guageMetric]
    # exemplar['timeUnixNano'] = timestamp
    # if traceId != None:
    #   exemplar['traceId'] = traceId
    # if spanId != None:
    #   exemplar['spanId'] = spanId
    # generatedMetric['gauge']['dataPoints'][0]['exemplars'].append(exemplar)

    generatedMetrics['resourceMetrics'][0]['scopeMetrics'][0]['metrics'].append(generatedMetric)
  return generatedMetrics

# example JSON to metrics
json_metric_array = [
    {
        "component_plies": [
            {
                "component_ply_id": "7",
                "component_ply_named_decimals": [],
                "max_mem_bytes": "157155328",
                "max_rss_bytes": "6119424",
                "mem_bytes": "157155328",
                "process_state": "RUNNING",
                "rss_bytes": "6119424",
                "system_cpu": "0.000",
                "user_cpu": "0.010"
            }
        ]
    },
    {
        "component_plies": [
            {
                "component_ply_id": "7",
                "component_ply_named_decimals": [
                    {
                        "MPHM": "5047248",
                        "MSHM": "409600",
                        "PHM": "5001264",
                        "SHM": "409600"
                    }
                ],
                "max_mem_bytes": "157155328",
                "max_rss_bytes": "6119424",
                "mem_bytes": "0",
                "process_state": "EXITED",
                "rss_bytes": "0",
                "system_cpu": "0.025",
                "user_cpu": "0.049"
            }
        ]
    }
]

METRIC_ATTRIBUTE_LABELS = ['component_ply_id', 'process_state']

def flatten(path, obj, results):
  if isinstance(obj, list):
    for item in obj:
      flatten(path, item, results)
  elif isinstance(obj, dict):
    for item in obj:
      flatten(path + "." + item, obj[item], results)
  else:
    results[path] = float(obj)

for json_metric_obj in json_metric_array:
    for k in json_metric_obj:
        print(k)
        for av in json_metric_obj[k]:
            print(av)
            attributes = {}
            for kk in av:
              if kk in METRIC_ATTRIBUTE_LABELS:
                  attributes[kk] = av[kk]
            gaugeMetrics = {}
            for kk in av:
              if kk not in METRIC_ATTRIBUTE_LABELS:
                flatten(k + "." + kk, av[kk], gaugeMetrics)
            resp = gen_synthetic_metric(serviceName='testService', timestamp=time.time_ns(), gaugeMetrics=gaugeMetrics, traceId='5B8EFFF798038103D269B633813FC60C', spanId='EEE19B7EC3C1B174', metricAttributes=attributes)
            print(resp)
            r = requests.post(f"{os.getenv('OTEL_EXPORTER_OTLP_HTTP_ENDPOINT')}/v1/metrics", json=resp)
            print(r)
            time.sleep(1)
    