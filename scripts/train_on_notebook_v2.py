import os
import subprocess
import sys
import glob

def run_cmd(cmd):
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing command: {result.stderr}")
    else:
        print(result.stdout)
    return result

# 1. Setup
print("--- Phase 1: Environment Setup ---")
subprocess.check_call([sys.executable, "-m", "pip", "install", "ultralytics"])

from ultralytics import YOLO

# 2. Data Sync
print("\n--- Phase 2: Synchronizing Data from S3 ---")
bucket_name = "wildlife-detection-sau-186224145570"
local_data_dir = os.path.join(os.getcwd(), "datasets", "elephant_data")
os.makedirs(local_data_dir, exist_ok=True)

# Sync specifically the images/labels subfolders
folders_to_sync = ["train", "val"]
for folder in folders_to_sync:
    print(f"Syncing {folder}...")
    run_cmd(["aws", "s3", "sync", f"s3://{bucket_name}/data/{folder}", os.path.join(local_data_dir, folder)])

# 3. Verify Structure
print("\n--- Phase 3: Verifying Local Structure ---")
for folder in folders_to_sync:
    img_path = os.path.join(local_data_dir, folder, "images")
    count = len(glob.glob(os.path.join(img_path, "*")))
    print(f"Folder {folder}/images contains {count} files.")
    if count == 0:
        print(f"WARNING: No files found in {img_path}")

# 4. Generate YAML
print("\n--- Phase 4: Generating Local YAML ---")
data_yaml_content = f"""
path: {local_data_dir}
train: train/images
val: val/images

names:
  0: elephant
"""
config_path = "config/notebook_data.yaml"
os.makedirs("config", exist_ok=True)
with open(config_path, "w") as f:
    f.write(data_yaml_content)
print(f"YAML created at {config_path}")

# 5. Training
print("\n--- Phase 5: Starting Training ---")
try:
    model = YOLO("yolo11n.pt")
    model.train(
        data=config_path,
        epochs=10,
        imgsz=640,
        batch=16,
        name="elephant_detection_notebook",
        project="training_results"
    )
    print("Training Complete!")
except Exception as e:
    print(f"CRITICAL ERROR during training: {e}")
