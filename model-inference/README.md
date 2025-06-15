# ML Ops Model Inference Deployment

This project implements a scalable model inference system using Ray Serve for deploying YOLOv8 models loaded from Weights & Biases (W&B) Model Registry.

## Solution Overview

The implemented solution consists of several key components:

1. **Ray Serve**: A scalable model serving framework for ML model deployment
2. **W&B Model Registry Integration**: Loading trained models from W&B Model Registry
3. **FastAPI Interface**: REST API for model inference
4. **Object Detection Service**: YOLOv8 model deployment with automatic scaling

## Setup Instructions

## Running Model Inference

### 1. Start Ray Serve

```bash
cd ray-deploy
python run_serve.py
```

This will:

- Initialize Ray cluster connection
- Load the model from W&B Model Registry
- Start the FastAPI service
- Enable automatic scaling based on load

### 2. Test the Deployment

```bash
cd test-deploy
python test.py
```

This test script will:

- Download a test image
- Send it to the inference service
- Process the detection results
- Save an annotated image with bounding boxes

### 3. Shutdown Ray Serve

To gracefully shut down the Ray Serve deployment:

```bash
RAY_ADDRESS='http://localhost:8265' serve shutdown
```

This command will:

- Stop all running deployments
- Release allocated resources
- Clean up the serving environment

## API Endpoints

### Object Detection

```
GET /detect?image_url=<url>
```

Response format:
```json
{
    "status": "found",
    "objects": [
        {
            "class": "object_name",
            "coordinates": [x1, y1, x2, y2]
        }
    ]
}
```

## Features

1. **Model Versioning**: Models are loaded from W&B Model Registry, ensuring version control
2. **Automatic Scaling**: Ray Serve handles load balancing and scaling
3. **Fallback Mechanism**: Falls back to base YOLOv8 model if W&B model loading fails
4. **REST API**: Easy-to-use HTTP interface for model inference
5. **Visualization**: Test script includes visualization of detection results
