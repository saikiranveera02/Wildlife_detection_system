import os
import sys
import time
import cv2
import asyncio
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO

# sys.path optimization for container
sys.path.append(os.path.join(os.getcwd(), 'src'))

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from lambda_handler import lambda_handler

app = FastAPI(title="Wildlife Guardian API")

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the Model Once
MODEL_PATH = "models/elephant_v1_97_accuracy.pt"
print("Loading AI Brain...")
try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Global state for the stream
current_video_path = None
use_webcam = False
alert_history = []
last_alert_time = 0
ALERT_COOLDOWN = 10  # Reduced for live demo excitement

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    global current_video_path, alert_history, use_webcam
    use_webcam = False # Disable webcam if file uploaded
    
    # Save the uploaded video temporarily
    upload_dir = "data/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    current_video_path = file_path
    alert_history = []  # Reset alerts for new video
    
    return {"message": "Video uploaded successfully", "filename": file.filename}

@app.post("/api/webcam/start")
async def start_webcam():
    global use_webcam, alert_history
    use_webcam = True
    alert_history = []
    return {"message": "Webcam mode activated"}

@app.get("/api/alerts")
def get_alerts():
    """Endpoint for React to poll for new alerts"""
    return JSONResponse(content={"alerts": alert_history})

def generate_frames():
    global current_video_path, use_webcam, last_alert_time, alert_history
    
    if use_webcam:
        cap = cv2.VideoCapture(0)
    elif current_video_path and os.path.exists(current_video_path):
        cap = cv2.VideoCapture(current_video_path)
    else:
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if model:
            # Run inference
            results = model.predict(source=frame, conf=0.5, verbose=False)
            elephant_detected = False
            confidence = 0.0
            annotated_frame = frame # Default if no results
            
            for result in results:
                # Always plot the bounding boxes for the frame
                annotated_frame = result.plot()
                
                # Check if an elephant was detected to trigger the alert
                for box in result.boxes:
                    if int(box.cls[0]) == 0:  # Elephant
                        elephant_detected = True
                        confidence = float(box.conf[0])
                        break
                
            # Trigger Alert Logic
            current_time = time.time()
            if elephant_detected and (current_time - last_alert_time) > ALERT_COOLDOWN:
                alert_msg = f"🐘 Elephant Detected! (Conf: {confidence:.0%})"
                print(f"🚨 [ALERT] {alert_msg}")
                
                alert_history.append({
                    "timestamp": time.strftime("%H:%M:%S"),
                    "message": alert_msg,
                    "confidence": confidence
                })
                
                # Trigger AWS Lambda
                cloud_event = {
                    "detections": [{"class": "elephant", "confidence": confidence}],
                    "image_uri": f"react_demo_capture_{int(current_time)}.jpg"
                }
                # Run in background to not block video stream
                try:
                    lambda_handler(cloud_event, None)
                    print("✅ AWS Alert Sent!")
                except Exception as e:
                    print(f"❌ Failed to send AWS Alert: {str(e)}")
                    
                last_alert_time = current_time
        else:
            annotated_frame = frame
            
        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()
        
        # Yield the frame in byte format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
               
        # Control playback speed (approx 30 FPS)
        time.sleep(0.03)

    cap.release()

@app.get("/api/video_feed")
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting Wildlife Guardian AI Backend...")
    print("API will be available at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
