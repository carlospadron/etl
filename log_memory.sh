#!/bin/bash

# Check if the container name or ID is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <container_id_or_name> [interval_seconds]"
  exit 1
fi

CONTAINER_ID=$1
INTERVAL=${2:-5}  # Default interval is 5 seconds if not provided

# Log memory usage to a file
LOG_FILE="memory_usage.log"
echo "Logging memory usage of container $CONTAINER_ID every $INTERVAL seconds to $LOG_FILE"
echo "Timestamp,MemoryUsage" > $LOG_FILE

while true; do
  TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
  MEMORY_USAGE=$(sudo docker stats --no-stream --format "{{.MemUsage}}" $CONTAINER_ID | awk '{print $1}')
  echo "$TIMESTAMP,$MEMORY_USAGE" >> $LOG_FILE
  echo "$TIMESTAMP,$MEMORY_USAGE"
  sleep $INTERVAL
done