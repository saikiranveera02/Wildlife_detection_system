import argparse
import subprocess

def train():
    # 1. Parse arguments passed from SageMaker
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=10)
    args, _ = parser.parse_known_args()

    # 2. Install necessary packages inside the container
    subprocess.check_call(["pip", "install", "ultralytics"])

    # 3. Setup paths
    dataset_config = "/opt/ml/input/data/training/config/data.yaml"
    
    # 4. Load model (using Nano for speed and cost efficiency)
    model = YOLO("yolo11n.pt") 

    # 5. Start training
    model.train(
        data=dataset_config,
        epochs=args.epochs,
        imgsz=640,
        batch=16,
        name="elephant_detection",
        project="/opt/ml/model",  # Save output to model directory
    )

if __name__ == "__main__":
    train()
