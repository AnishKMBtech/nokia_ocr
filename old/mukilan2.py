import cv2
from paddleocr import PaddleOCR
import time
import numpy as np
import requests
import os

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')  # GPU will be used if available

# Load image from file
image_path = "source.jpg"
frame = cv2.imread(image_path)

if frame is None:
    print(f"Error: Could not read image file: {image_path}")
    exit()

# Resize image for potentially better OCR accuracy
frame_resized = cv2.resize(frame, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
results = ocr.ocr(frame_resized, cls=True)

if results and results[0]:
    for line in results[0]:
        bbox = line[0]
        text = line[1][0]
        confidence = line[1][1]

        if confidence >= 0.90:  # Only high confidence
            # Adjust bounding box coordinates back to original frame size
            top_left = tuple(map(int, (bbox[0][0] / 2.0, bbox[0][1] / 2.0)))
            bottom_right = tuple(map(int, (bbox[2][0] / 2.0, bbox[2][1] / 2.0)))
            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(frame, text, (top_left[0], top_left[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Send to backend
            url = 'http://localhost:3000/save-ocr'
            data = {
                'imageName': os.path.basename(image_path), # Use the actual image name
                'detectedText': text,
                'confidence': round(confidence * 100, 2)
            }
            try:
                response = requests.post(url, json=data)
                if response.status_code == 200:
                    print(f"✔ OCR: {text} ({round(confidence * 100, 2)}%) sent to DB.")
                else:
                    print(f"✖ DB Error: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"✖ Server connection failed: {e}")

            # Save locally
            # Define the local file path relative to the script's directory
            local_filename = "ocr_detected_text.txt"
            file_path = os.path.join(os.path.dirname(__file__), local_filename)
            # No need for os.makedirs if saving in the current directory
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write(f"Text: {text}, Confidence: {round(confidence * 100, 2)}%, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

# Show overlay with bounding boxes
cv2.imshow("Image with OCR", frame)
print("Press any key to close the image window.")
cv2.waitKey(0) # Wait indefinitely until a key is pressed
cv2.destroyAllWindows()