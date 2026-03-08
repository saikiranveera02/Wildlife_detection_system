# Elephant Training Script for SageMaker Notebook
import os
import subprocess

# 1. Install Ultralytics
print("Installing Ultralytics...")
subprocess.check_call(["pip", "install", "ultralytics"])

from ultralytics import YOLO

# 2. Download Data from S3 (Workaround for local notebook access)
print("Downloading data from S3...")
bucket_name = "wildlife-detection-sau-186224145570"
subprocess.run(["aws", "s3", "sync", f"s3://{bucket_name}/data", "datasets/elephant_data"])

# 3. Create/Update local data.yaml for the notebook
# We create a local version that points to the folder we just downloaded
data_yaml_content = f"""
path: /home/ec2-user/elephant_project/datasets/elephant_data
train: train/images
val: val/images

names:
  0: elephant
"""
with open("config/notebook_data.yaml", "w") as f:
    f.write(data_yaml_content)

dataset_config = "config/notebook_data.yaml"

# 4. Load Model
print("Loading YOLOv11n...")
model = YOLO("yolo11n.pt")

# 5. Train
print("Starting Training...")
model.train(
    data=dataset_config,
    epochs=10,
    imgsz=640,
    batch=16,
    name="elephant_detection_notebook",
    project="training_results"
)

print("Training Complete! Weight saved in training_results/elephant_detection_notebook/weights/best.pt")
