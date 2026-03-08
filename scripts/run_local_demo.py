import cv2
import os
import sys
import time
from ultralytics import YOLO

# --- ANACONDA SSL HOTFIX ---
# Fixes 'ssl' import error when using boto3 inside a standard venv built from Anaconda
conda_lib = r"C:\Users\saiki\anaconda3\Library\bin"
if os.path.exists(conda_lib):
    os.environ["PATH"] = conda_lib + os.pathsep + os.environ.get("PATH", "")
# ---------------------------

# Add src to path so we can import lambda_handler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from lambda_handler import lambda_handler

def run_demo(video_path):
    print("--- 🐘 Starting Local Video AI Demo ---")
    
    # 1. Load the Model
    model_path = "models/elephant_v1_97_accuracy.pt"
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}. Download it first!")
        return
    print("Loading AI Brain...")
    model = YOLO(model_path)

    # 2. Open the Video Stream
    print(f"Opening Video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return

    # 3. Alert Cooldown Settings
    # We do not want to trigger AWS SNS 30 times a second if an elephant is on screen!
    last_alert_time = 0
    alert_cooldown_seconds = 30  # Wait 30 seconds before sending another SMS

    print("\nStarting Scanning Engine. Press 'q' on your keyboard to stop.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Video ended or stream lost.")
            break

        # Run AI inference on the current frame
        # Conf=0.7 means we only care if AI is 70% sure it's an elephant
        results = model.predict(source=frame, conf=0.7, verbose=False)
        
        # Check if an elephant was detected
        elephant_detected = False
        confidence = 0.0
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Class 0 is Elephant
                if int(box.cls[0]) == 0:
                    elephant_detected = True
                    confidence = float(box.conf[0])
                    break
            
            # Draw the bounding boxes on the video frame
            annotated_frame = result.plot()
        
        # Display the video with AI boxes
        cv2.imshow('Wildlife Guardian - Live View', annotated_frame)

        # Trigger AWS Event if Elephant is detected AND cooldown has passed
        current_time = time.time()
        if elephant_detected and (current_time - last_alert_time) > alert_cooldown_seconds:
            print(f"\n🚨 [ALERT] Elephant Detected! (Confidence: {confidence:.2f})")
            print("Triggering AWS Village Alert System...")
            
            # Mock the S3 URL since the video is local
            mock_s3_url = f"local_demo_capture_{int(current_time)}.jpg"
            
            # Create the payload expected by our Lambda
            cloud_event = {
                "detections": [{"class": "elephant", "confidence": confidence}],
                "image_uri": mock_s3_url
            }
            
            # Trigger Lambda directly
            response = lambda_handler(cloud_event, None)
            print(f"AWS Response: {response['statusCode']}")
            
            # Reset Cooldown Timer
            last_alert_time = current_time

        # Press 'q' to quit the video stream
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("Demo Shutdown Complete.")

if __name__ == "__main__":
    # Change this path to the video you want to test!
    # If you want to use your laptop Webcam, change it to: video_file = 0
    video_file = r"C:\Users\saiki\Downloads\elephant video.mp4"
    run_demo(video_file)
