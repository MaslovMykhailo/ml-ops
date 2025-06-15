import os
import time
from typing import Dict, Any

import cv2
import numpy as np
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from ultralytics import YOLO

# OpenTelemetry monitoring
from monitoring.otel_collector import YOLOOpenTelemetryCollector

app = FastAPI(title="YOLO11 Detection API", version="3.0.0")

# Model
MODEL_NAME = "yolo11n"
model = YOLO(f"{MODEL_NAME}.pt")

# OpenTelemetry collector
try:
    otel_collector = YOLOOpenTelemetryCollector()
    print("✅ OpenTelemetry monitoring enabled")
except Exception as e:
    print(f"❌ OpenTelemetry failed: {e}")
    otel_collector = None

@app.get("/")
async def root():
    return {
        "message": "YOLO11 Detection API",
        "model": MODEL_NAME,
        "monitoring": "OpenTelemetry → ClickHouse → Grafana",
        "endpoints": ["/detect", "/health"]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "model": f"{MODEL_NAME}.pt",
        "monitoring": "opentelemetry" if otel_collector else "disabled"
    }

@app.post("/detect")
async def detect_objects(file: UploadFile = File(...)) -> Dict[str, Any]:
    start_time = time.time()
    
    # Validation
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Load and decode image
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # YOLO detection
        results = model(image)[0]
        processing_time = (time.time() - start_time) * 1000
        
        # Process results
        detections = []
        if results.boxes is not None:
            boxes = results.boxes.xyxy.cpu().numpy()
            confidences = results.boxes.conf.cpu().numpy()
            class_ids = results.boxes.cls.cpu().numpy().astype(int)
            
            for box, confidence, class_id in zip(boxes, confidences, class_ids):
                x1, y1, x2, y2 = box
                detections.append({
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "confidence": float(confidence),
                    "class_name": model.names[class_id]
                })
        
        # Write to ClickHouse via OpenTelemetry
        if otel_collector:
            try:
                await otel_collector.record_prediction(
                    image, detections, processing_time, 
                    file.filename or "unknown", MODEL_NAME
                )
            except Exception:
                pass  # Don't block API
        
        # Response
        return {
            "success": True,
            "processing_time_ms": round(processing_time, 2),
            "objects_detected": len(detections),
            "detections": detections
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 YOLO11 API starting on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 