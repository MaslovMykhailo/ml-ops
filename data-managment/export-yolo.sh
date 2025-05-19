#!/bin/bash
set -e

PROJECT_ID=${1:-1}  # Default project ID is 1
PROJECT_VERSION=${2:-v1}  # Default project version is v1
OUTPUT_FILE="dataset/yolo_export.zip"  # Default output filename

if [ -z "$REFRESH_TOKEN" ]; then
  echo "Error: REFRESH_TOKEN environment variable is not set."
  echo "Usage: export REFRESH_TOKEN=your_token"
  echo "Then run: ./export_yolo.sh [project_id]"
  exit 1
fi

echo "Getting access token..."
ACCESS_TOKEN=$(curl -s -X POST http://localhost:8080/api/token/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH_TOKEN\"}" | grep -o '"access":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "Error: Failed to get access token. Check your refresh token and Label Studio availability."
  exit 1
fi

echo "Exporting data from project #${PROJECT_ID} in YOLO format..."
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  "http://localhost:8080/api/projects/$PROJECT_ID/export?exportType=YOLO_WITH_IMAGES" \
  -o "$OUTPUT_FILE"

if [ -s "$OUTPUT_FILE" ]; then
  echo "Export successful! File saved as $OUTPUT_FILE"
else
  echo "Error: Export failed or no data was exported."
  exit 1
fi

echo "Unzipping the exported data..."
unzip -o "$OUTPUT_FILE" -d dataset/$PROJECT_VERSION

if [ $? -ne 0 ]; then
  echo "Error: Failed to unzip the exported data."
  exit 1
fi
echo "Cleaning up..."
rm "$OUTPUT_FILE"

echo "Done. You can now use the exported data for your YOLO model training." 