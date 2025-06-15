import cv2
import numpy as np
import requests

# Test image URL (receipt image for testing)
image_url = "https://pandapaperroll.com/wp-content/uploads/2020/05/Receipt-paper-types-1.jpg"
server_url = "http://localhost:8000/detect"

# Download and decode the image
resp = requests.get(image_url)
image_nparray = np.asarray(bytearray(resp.content), dtype=np.uint8)
image = cv2.imdecode(image_nparray, cv2.IMREAD_COLOR)

# Send request to the object detection server
resp = requests.get(f"{server_url}?image_url={image_url}")
detections = resp.json()["objects"]

# Draw bounding boxes and labels for each detected object
for item in detections:
    class_name = item["class"]
    coords = item["coordinates"]

    # Draw rectangle around detected object
    cv2.rectangle(image, (int(coords[0]), int(coords[1])), (int(coords[2]), int(coords[3])), (0, 0, 0), 2)

    # Add class label above the bounding box
    cv2.putText(image, class_name, (int(coords[0]), int(coords[1] - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

# Save the annotated image
cv2.imwrite("output.jpeg", image)