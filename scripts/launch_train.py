import boto3
import sagemaker
from sagemaker.pytorch import PyTorch

# Initialize SageMaker session
sagemaker_session = sagemaker.Session()
role = "arn:aws:iam::186224145570:role/SageMakerExecutionRole"

# S3 paths
bucket = "wildlife-detection-sau-186224145570"
dataset_s3 = f"s3://{bucket}/data"

# Setup Estimator
estimator = PyTorch(
    entry_point="train_sagemaker.py",
    source_dir="src",
    role=role,
    framework_version="2.0",
    py_version="py310",
    instance_count=1,
    instance_type="ml.m5.xlarge", # Cost effective choice
    hyperparameters={
        "epochs": 10
    },
)

# Start Job
print("Launching SageMaker Training Job...")
estimator.fit({"training": dataset_s3})
