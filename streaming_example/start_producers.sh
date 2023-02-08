#!/bin/bash
# Start the producers
python -c  produce_avro.py
python -c  produce_json.py