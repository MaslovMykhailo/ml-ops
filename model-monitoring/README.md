# ML Model Monitoring System

Machine learning monitoring system based on YOLO with complete observability stack: performance metrics, data drift detection, and visualization.

## System Components

- **YOLO API**: FastAPI service for object detection
- **OpenTelemetry Collector**: Metrics and traces collection
- **ClickHouse**: Analytics database
- **Grafana**: Dashboards and metrics visualization
- **Prometheus**: System resource monitoring
- **Evidently**: Data drift detection
- **Test Client**: Testing utilities

### System Deployment

```bash
# Clone and start all services
cd model-monitoring
docker compose up --build -d
```

### Service Access

After startup, services will be available at the following addresses:

| Service | URL | Description |
|---------|-----|-------------|
| **YOLO API** | http://localhost:30080 | Object detection API |
| **ClickHouse** | http://localhost:30123 | Database (Web UI: /play) |
| **Prometheus** | http://localhost:30091 | System metrics |
| **Grafana** | http://localhost:30001 | Dashboards (admin/admin) |

## 📊 Metrics Monitoring

The system automatically collects and displays the following metrics:

### Core Model Metrics

- **Predictions per minute** - API usage frequency
- **Average processing time** - model performance
- **Object class distribution** - what's detected most frequently
- **Confidence level** - prediction quality

### System Metrics

- CPU and memory of containers
- Network traffic
- Service status

## 🔍 Model Usage

### 1. curl command

```bash
curl -X POST http://localhost:30080/detect \
     -F "file=input/8.jpg"
```

### 2. Python client (local file)

```bash
python test/client.py input/1.jpg
```

### 3. Python client (URL)

```bash
python test/client.py https://example.com/image.jpg
```

### 4. Bulk testing

```bash
python test/test.py
```

### API Health Check

```bash
curl http://localhost:30080/health
```

## 📈 Grafana Dashboards

After system startup, open Grafana at http://localhost:30001 (admin/admin).

Available dashboards:

- **YOLO Model Performance** - real-time model metrics
- **System Resources** - resource usage
- **API Health** - service status and availability

## 🚨 Data Drift Detection

The system supports data drift detection using Evidently AI.

### Environment Setup

Create a `.env` file in the `model-monitoring/` directory:

```env
# Evidently Cloud (create account at https://www.evidentlyai.com/)
EVIDENTLY_API_KEY=your_api_key_here
EVIDENTLY_PROJECT_ID=your_project_id
EVIDENTLY_PROJECT_NAME=YOLO_Monitoring

# ClickHouse (defaults)
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=30900
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=

# Analysis configuration
REFERENCE_CLASS_NAME=book
REFERENCE_MIN_CONFIDENCE=0.8
REFERENCE_LIMIT=10
CURRENT_DAYS_AGO=7
```

### Creating Reference Dataset

```bash
cd evidently
python create_reference_dataset.py
```

This command:

- Extracts data from ClickHouse
- Creates a reference dataset in Evidently Cloud
- Saves the dataset ID for future use

### Running Drift Analysis

```bash
python drift_analyzer.py
```

Result will be available at: https://app.evidently.cloud/projects/your_project/reports/your_report

### Stop System

```bash
docker compose down
```
