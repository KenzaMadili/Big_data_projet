#!/bin/bash

echo "Creating HDFS directories..."
hdfs dfs -mkdir -p /user/logs/raw/date=2025-01-10/normal
hdfs dfs -mkdir -p /user/logs/raw/date=2025-01-10/anomaly

echo "Uploading logs to HDFS..."
hdfs dfs -put -f ../data/raw/date=2025-01-10/normal/*.json /user/logs/raw/date=2025-01-10/normal/
hdfs dfs -put -f ../data/raw/date=2025-01-10/anomaly/*.json /user/logs/raw/date=2025-01-10/anomaly/

echo "Upload completed successfully"
