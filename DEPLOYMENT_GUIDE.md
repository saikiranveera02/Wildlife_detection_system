# AWS Deployment Guide - AI Wildlife Detection System

This guide outlines the complete process followed to containerize and deploy the AI Wildlife Detection System to AWS.

## Architecture Overview
- **Frontend**: React (Vite) hosted on **AWS S3 Static Website**.
- **Backend API**: FastAPI + YOLOv11 hosted on **AWS App Runner**.
- **AI Engine**: Ultralytics YOLOv11 (CPU-optimized).
- **Storage & Alerts**: AWS DynamoDB (logs) and AWS SNS (notifications).

---

## Step 1: Containerization (Docker)
We used a multi-stage approach to optimize the backend image for AWS App Runner.

### 1.1 Base Image Selection
We switched from a standard Python image to the official Ultralytics CPU image to ensure stability and pre-installed dependencies.
```dockerfile
FROM ultralytics/ultralytics:latest-cpu
```

### 1.2 Environment Configuration
Added regional defaults within the Dockerfile to prevent `boto3` initialization failures.
```dockerfile
ENV AWS_DEFAULT_REGION=us-east-1
```

### 1.3 Deployment Command
```bash
docker build -t wildlife-backend .
docker tag wildlife-backend:latest <ECR_URL>:latest
docker push <ECR_URL>:latest
```

---

## Step 2: AWS Backend Deployment (App Runner)

### 2.1 IAM Role Configuration
Two critical roles were configured:
1.  **AppRunnerECRAccessRole**: Grants App Runner permission to pull images from ECR.
    - Policy: `AWSAppRunnerServicePolicyForECRAccess`
2.  **SageMakerExecutionRole** (Instance Role): Grants the running container access to AWS services.
    - Policies: `AmazonSNSFullAccess`, `AmazonDynamoDBFullAccess`, `AmazonS3FullAccess`

### 2.2 Service Creation
The service was created using a JSON configuration specifying 1 vCPU and 2GB RAM to handle the YOLOv11 model load.

---

## Step 3: Frontend Deployment (S3)

### 3.1 Build Optimization
Updated `API_BASE_URL` in `Dashboard.jsx` to the live App Runner endpoint: `https://qkzpmdfc6f.us-east-1.awsapprunner.com/api`.

### 3.2 S3 Sync
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://wildlife-ai-dashboard-2026/ --region us-east-1
```

---

## Step 4: Troubleshooting & Fixes
- **Regional Errors**: Fixed `NoRegionError` by explicitly passing `region_name='us-east-1'` to `boto3.client`.
- **Permission Errors**: Fixed `Invalid Access Role` by attaching the correct service-linked policy to the ECR Access Role.
- **Dependency Issues**: Switched to `opencv-python-headless` and CPU-only PyTorch to reduce image size from 5GB+ to ~1GB.

---

## Live Endpoints
- **Web Dashboard**: [http://wildlife-ai-dashboard-2026.s3-website-us-east-1.amazonaws.com](http://wildlife-ai-dashboard-2026.s3-website-us-east-1.amazonaws.com)
- **API Endpoint**: [https://qkzpmdfc6f.us-east-1.awsapprunner.com](https://qkzpmdfc6f.us-east-1.awsapprunner.com)
