import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

logger = logging.getLogger(__name__)

class YOLOOpenTelemetryCollector:
    """
    OpenTelemetry collector for YOLO predictions.
    Records only spans with data about each prediction.
    """
    
    def __init__(self, 
                 service_name: str = "yolo-detection-api",
                 otel_endpoint: str = "http://otel-collector:4318",
                 instance_id: Optional[str] = None):
        
        self.session_id = str(uuid.uuid4())
        self.instance_id = instance_id or f"yolo-{uuid.uuid4().hex[:8]}"
        self.service_name = service_name
        
        resource = Resource.create({
            "service.name": service_name,
            "service.instance.id": self.instance_id,
        })
        
        try:
            # Configure trace provider
            trace.set_tracer_provider(TracerProvider(resource=resource))
            
            # OTLP span exporter
            span_exporter = OTLPSpanExporter(
                endpoint=f"{otel_endpoint}/v1/traces"
            )
            
            # Batch span processor
            span_processor = BatchSpanProcessor(
                span_exporter,
                max_queue_size=256,
                max_export_batch_size=32,
                export_timeout_millis=3000,
                schedule_delay_millis=1000
            )
            
            trace.get_tracer_provider().add_span_processor(span_processor)
            self.tracer = trace.get_tracer(__name__)
            
            print(f"✅ OpenTelemetry: {service_name} [{self.instance_id}]")
            
        except Exception as e:
            print(f"❌ OpenTelemetry failed: {e}")
            self.tracer = None
    
    async def record_prediction(self, 
                               image: Any,
                               detections: List[Dict],
                               processing_time_ms: float,
                               filename: str = "unknown",
                               model_name: str = "yolo11n",
                               confidence_threshold: float = 0.90) -> Optional[str]:
        """
        Records prediction data in a span.
        """
        
        if not self.tracer:
            return None
        
        prediction_id = str(uuid.uuid4())
        
        # Create span with prediction data
        with self.tracer.start_as_current_span("yolo_prediction") as span:
            try:
                # Get image dimensions
                height, width = image.shape[:2] if hasattr(image, 'shape') else (0, 0)
                
                # Set main attributes for the span
                span.set_attributes({
                    "prediction_id": prediction_id,
                    "timestamp": datetime.now().isoformat(),
                    "processing_time_seconds": processing_time_ms / 1000.0,
                    "image_width": width,
                    "image_height": height,
                    "total_objects": len(detections),
                    "filename": filename,
                    "model_name": model_name
                })
                
                # Add each object as an event to the span
                for i, detection in enumerate(detections):
                    bbox = detection.get('bbox', [0, 0, 0, 0])
                    span.add_event(
                        name="object_detected",
                        attributes={
                            "object_index": i,
                            "class_name": detection.get('class_name', 'unknown'),
                            "confidence": detection.get('confidence', 0.0),
                            "bbox_x1": bbox[0],
                            "bbox_y1": bbox[1],
                            "bbox_x2": bbox[2],
                            "bbox_y2": bbox[3]
                        }
                    )
                
                print(f"📊 OTEL: {len(detections)} objects | {processing_time_ms:.0f}ms")
                return prediction_id
                
            except Exception as e:
                span.record_exception(e)
                logger.error(f"OTEL recording failed: {e}")
                return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Returns information about the current collector.
        """
        return {
            "status": "initialized" if self.tracer else "failed",
            "instance_id": self.instance_id
        }
    
    def close(self):
        """
        Closes and shuts down OpenTelemetry.
        """
        try:
            if self.tracer:
                trace.get_tracer_provider().shutdown()
        except Exception as e:
            logger.error(f"OTEL close error: {e}") 