import os
from ultralytics import YOLO
import glob
import random

def test_local_model():
    print("--- 🐘 Starting Local Elephant Detection Test ---")
    
    model_path = "models/elephant_v1_97_accuracy.pt"
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        print("Make sure you downloaded it from S3 first!")
        return

    print("1. Loading the trained 'Brain'...")
    try:
        model = YOLO(model_path)
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    print(f"\n2. Finding the test image...")
    # Using the specific image provided by the user
    test_img = r"C:\Users\saiki\Downloads\elephant u=image.jpg"
    
    if not os.path.exists(test_img):
        print(f"Error: Could not find image at {test_img}")
        return
        
    print(f"Selected image: {test_img}")

    print("\n3. Running the AI scan...")
    # Run inference and explicitly save the result image
    results = model.predict(source=test_img, save=True, project="runs", name="local_test", exist_ok=True)
    
    print("\n--- ✅ Test Complete! ---")
    print("The model has analyzed the image.")
    print("To see the result (with bounded boxes drawn), open the newly created 'runs/local_test' folder in your project directory.")

if __name__ == "__main__":
    test_local_model()
