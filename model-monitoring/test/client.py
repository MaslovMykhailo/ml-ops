import requests
import sys
import json
import cv2
import os
import numpy as np
from pathlib import Path
from urllib.parse import urlparse

API_URL = "http://localhost:30080"

def check_health():
    """Check API health status"""
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data['status']}")
            print(f"   Model: {data['model']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def download_image_from_url(url):
    """Download image from URL"""
    try:
        print(f"📥 Downloading image from URL...")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Convert to numpy array for OpenCV
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if image is None:
            print(f"❌ Failed to decode image from URL")
            return None
            
        print(f"✅ Image successfully downloaded")
        return image, response.content
        
    except Exception as e:
        print(f"❌ Error downloading image: {e}")
        return None, None

def draw_detections(image, detections, output_path):
    """Draw bounding boxes on the image"""
    try:
        # Colors for different classes (BGR format)
        colors = [
            (0, 255, 0),    # Green
            (255, 0, 0),    # Blue  
            (0, 0, 255),    # Red
            (255, 255, 0),  # Cyan
            (255, 0, 255),  # Purple
            (0, 255, 255),  # Yellow
        ]
        
        # Create a copy of the image for annotations
        annotated_image = image.copy()
        
        # Draw each detection
        for i, detection in enumerate(detections):
            bbox = detection['bbox']
            class_name = detection['class_name']
            confidence = detection['confidence']
            
            # Bounding box coordinates
            x1, y1, x2, y2 = map(int, bbox)
            
            # Color selection
            color = colors[i % len(colors)]
            
            # Draw rectangle
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)
            
            # Prepare text
            label = f"{class_name}: {confidence:.2f}"
            
            # Text size
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            thickness = 2
            (text_width, text_height), _ = cv2.getTextSize(label, font, font_scale, thickness)
            
            # Text background
            cv2.rectangle(annotated_image, (x1, y1 - text_height - 10), (x1 + text_width, y1), color, -1)
            
            # Text
            cv2.putText(annotated_image, label, (x1, y1 - 5), font, font_scale, (255, 255, 255), thickness)
        
        # Save result
        cv2.imwrite(output_path, annotated_image)
        print(f"📸 Annotated image saved: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error drawing detections: {e}")
        return False

def load_local_image(image_path):
    """Load local image"""
    try:
        print(f"📥 Loading local image...")
        if not os.path.exists(image_path):
            print(f"❌ File not found: {image_path}")
            return None, None
            
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Failed to read image: {image_path}")
            return None, None
            
        # Convert to bytes for sending
        _, image_bytes = cv2.imencode('.jpg', image)
        image_bytes = image_bytes.tobytes()
        
        print(f"✅ Image successfully loaded")
        return image, image_bytes
        
    except Exception as e:
        print(f"❌ Error loading image: {e}")
        return None, None

def detect_objects(image_input):
    """General function for object detection from URL or local file"""
    try:
        # Determine input type and load image
        if is_url(image_input):
            image, image_bytes = download_image_from_url(image_input)
        else:
            image, image_bytes = load_local_image(image_input)
            
        if image is None or image_bytes is None:
            return None, None
        
        # Send to API
        print(f"🔍 Sending image to API...")
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
        response = requests.post(f"{API_URL}/detect", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Detection completed!")
            print(f"   Processing time: {data['processing_time_ms']:.1f}ms")
            print(f"   Objects detected: {data['objects_detected']}")
            
            # Show all detections
            if data['detections']:
                print(f"\n🔍 Detected objects:")
                for i, detection in enumerate(data['detections'], 1):
                    bbox = detection['bbox']
                    print(f"   {i}. {detection['class_name']}: {detection['confidence']:.3f}")
                    print(f"      bbox: [{bbox[0]:.0f}, {bbox[1]:.0f}, {bbox[2]:.0f}, {bbox[3]:.0f}]")
            
            return data, image
        else:
            print(f"❌ Detection failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def is_url(string):
    """Check if string is a URL"""
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except:
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python client.py <image_URL or file_path>")
        print("Examples:")
        print("  python client.py https://ultralytics.com/images/bus.jpg")
        print("  python client.py ./images/local_image.jpg")
        sys.exit(1)
    
    image_input = sys.argv[1]
    
    print("🚀 YOLO11 Detection Client")
    print("=" * 40)
    
    # Check API health
    if not check_health():
        print("💡 Make sure API is running: python app.py")
        sys.exit(1)
    
    print()
    
    # Object detection
    result, image = detect_objects(image_input)
    
    if result and result['detections'] and image is not None:
        print(f"\n📄 Full response:")
        print(json.dumps(result, indent=2))
        
        # Create output filename
        if is_url(image_input):
            parsed_url = urlparse(image_input)
            filename = os.path.basename(parsed_url.path) or "image.jpg"
        else:
            filename = os.path.basename(image_input)
            
        path = Path(filename)
        output_path = os.path.join("output", f"{path.stem}_detected{path.suffix}")
        
        # Draw bounding boxes for all detections
        if draw_detections(image, result['detections'], output_path):
            print(f"✨ Done! Check the annotated image: {output_path}")
        
    elif result and result['objects_detected'] == 0:
        print("ℹ️  No objects detected in the image")
    else:
        print("❌ Detection failed or no results")

if __name__ == "__main__":
    main() 