import requests
import sys
import json
import cv2
import os
import numpy as np
from pathlib import Path
import glob
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
        print(f"📥 Loading local image: {os.path.basename(image_path)}")
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

def detect_objects(image_path):
    """Perform object detection on a single image"""
    try:
        # Load image
        image, image_bytes = load_local_image(image_path)
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

def get_images_from_folder(input_folder, file_extension):
    """Get all images from folder with specified extension"""
    try:
        # Normalize extension (add dot if missing)
        if not file_extension.startswith('.'):
            file_extension = '.' + file_extension
        
        # Create search pattern
        pattern = os.path.join(input_folder, f"*{file_extension}")
        
        # Find all matching files
        image_files = glob.glob(pattern, recursive=False)
        
        # Also search case-insensitive
        pattern_upper = os.path.join(input_folder, f"*{file_extension.upper()}")
        image_files.extend(glob.glob(pattern_upper, recursive=False))
        
        # Remove duplicates and sort
        image_files = sorted(list(set(image_files)))
        
        print(f"📁 Found {len(image_files)} images with extension '{file_extension}' in '{input_folder}'")
        return image_files
        
    except Exception as e:
        print(f"❌ Error searching for images: {e}")
        return []

def process_images(input_folder, file_extension, output_folder="output"):
    """Process all images in the input folder"""
    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all images with specified extension
    image_files = get_images_from_folder(input_folder, file_extension)
    
    if not image_files:
        print(f"❌ No images found with extension '{file_extension}' in '{input_folder}'")
        return
    
    # Process each image
    total_images = len(image_files)
    successful_detections = 0
    
    for i, image_path in enumerate(image_files, 1):
        print(f"\n{'='*50}")
        print(f"Processing image {i}/{total_images}: {os.path.basename(image_path)}")
        print(f"{'='*50}")
        
        # Perform object detection
        result, image = detect_objects(image_path)
        
        if result and image is not None:
            # Create output filename
            path = Path(image_path)
            output_path = os.path.join(output_folder, f"{path.stem}_detected{path.suffix}")
            
            if result['detections']:
                # Draw bounding boxes
                if draw_detections(image, result['detections'], output_path):
                    successful_detections += 1
                    print(f"✨ Annotated image saved!")
            else:
                # Save original image even if no detections
                cv2.imwrite(output_path, image)
                print(f"ℹ️  No objects detected - saved original image")
                successful_detections += 1
                
        else:
            print(f"❌ Failed to process image: {os.path.basename(image_path)}")
    
    # Summary
    print(f"\n{'='*50}")
    print(f"📊 PROCESSING SUMMARY")
    print(f"{'='*50}")
    print(f"Total images processed: {total_images}")
    print(f"Successful detections: {successful_detections}")
    print(f"Failed detections: {total_images - successful_detections}")
    print(f"Output folder: {output_folder}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python test.py <input_folder> <file_extension>")
        print("Examples:")
        print("  python test.py ./images jpg")
        print("  python test.py /path/to/images .png")
        print("  python test.py ../data jpeg")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    file_extension = sys.argv[2]
    
    print("🚀 YOLO11 Batch Detection Test")
    print("=" * 50)
    print(f"Input folder: {input_folder}")
    print(f"File extension: {file_extension}")
    print("=" * 50)
    
    # Check if input folder exists
    if not os.path.exists(input_folder):
        print(f"❌ Input folder does not exist: {input_folder}")
        sys.exit(1)
    
    if not os.path.isdir(input_folder):
        print(f"❌ Path is not a directory: {input_folder}")
        sys.exit(1)
    
    # Check API health
    if not check_health():
        print("💡 Make sure API is running: python app.py")
        sys.exit(1)
    
    print()
    
    # Process all images
    process_images(input_folder, file_extension)

if __name__ == "__main__":
    main()
