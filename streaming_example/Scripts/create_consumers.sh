#!/bin/bash

docker exec kafkacat kafkacat -b kafka:9092 -t demo.products -C -o -u -q -r http://schema-registry:8085 -s avro

docker exec kafkacat kafkacat -b kafka:9092 -t demo.purchases -C -o -u -q -r http://schema-registry:8085 -s avro


#https://itnext.io/exploring-popular-open-source-stream-processing-technologies-part-1-of-2-31069337ba0e