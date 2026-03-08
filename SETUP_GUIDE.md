# Project Setup & Configuration Guide: Wildlife Detection System

This document serves as a comprehensive record of the steps and commands followed to initialize the project and configure the AWS environment for Elephant Detection.

## Phase 1: Local Project Initialization

### 1. Project Directory Structure
We created a modular directory structure to organize source code, models, tests, and data.

**Command:**
```powershell
mkdir src, src/models, src/utils, tests, models, config, data, scripts
```

### 2. Dependency Management
We initialized a `requirements.txt` file with the necessary libraries for AI, AWS integration, and testing.

**File Contents (`requirements.txt`):**
- `ultralytics` (YOLOv8)
- `pydantic` (Data Validation)
- `boto3` (AWS SDK)
- `pytest` & `hypothesis` (Testing)
- `opencv-python` (Image Processing)
- `pyyaml`, `pandas`, `matplotlib`

---

## Phase 2: AWS CLI Setup & Configuration

### 1. Installation
The AWS CLI was installed using the MSI installer.

**Verification Command:**
```powershell
aws --version
```

### 2. Identity & Access Management (IAM)
We created a dedicated user to manage project resources safely.
- **User Name:** `wildlife-admin`
- **Permissions:** `AdministratorAccess` (attached directly)
- **Access Keys:** Generated a `.csv` file containing the `Access Key ID` and `Secret Access Key`.

### 3. CLI Configuration
We linked the local environment to the AWS account using the generated credentials.

**Command:**
```powershell
aws configure
# Inputs provided:
# AWS Access Key ID: [From CSV]
# AWS Secret Access Key: [From CSV]
# Default region name: us-east-1
# Default output format: json
```

### 4. Connection Verification
We verified that the CLI can communicate with AWS and identified the active user.

**Command:**
```powershell
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" sts get-caller-identity
```

---

## Phase 3: AWS Resource Creation (Cloud Infrastructure)

### 1. S3 Bucket Creation
We created a unique S3 bucket to store all project-related assets in the cloud.

**Command:**
```powershell
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" s3 mb s3://wildlife-detection-sau-186224145570 --region us-east-1
```

### 2. Cloud Folder Structure
We initialized specific "folders" (prefixes) within the S3 bucket to organize data.

**Commands:**
```powershell
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" s3api put-object --bucket wildlife-detection-sau-186224145570 --key data/train/
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" s3api put-object --bucket wildlife-detection-sau-186224145570 --key data/val/
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" s3api put-object --bucket wildlife-detection-sau-186224145570 --key models/
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" s3api put-object --bucket wildlife-detection-sau-186224145570 --key uploads/
```

---

## Phase 4: Dataset Preparation

### 1. Unzipping the Dataset
If the dataset is in a zip file, it must be extracted into the local project structure.

**Command:**
```powershell
Expand-Archive -Path "C:\Users\saiki\Downloads\archive (3).zip" -DestinationPath "c:\Users\saiki\Wildlife_detection_system\wildlife-detection-system\data"
```

### 2. Organizing the Dataset (Windows PowerShell)
The zip file extracted into a subfolder. We moved the files into the standard `data/` structure and renamed `valid` to `val`.

**Commands:**
```powershell
Move-Item -Path "data\elephant-dataset-yolov\train", "data\elephant-dataset-yolov\test", "data\elephant-dataset-yolov\valid" -Destination "data\"
Rename-Item -Path "data\valid" -NewName "val"
Remove-Item -Path "data\elephant-dataset-yolov" -Recurse
```

### 3. S3 Synchronization
Sync everything to the cloud.

**Command:**
```powershell
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" s3 sync c:\Users\saiki\Wildlife_detection_system\wildlife-detection-system\data s3://wildlife-detection-sau-186224145570/data
```

---

## Phase 5: Understanding the Dataset Format

For this project, we are using the **YOLOv8** format, which consists of two main components:

### 1. Folder Structure
- **`images/`**: Contains the raw photos (JPG/PNG).
- **`labels/`**: Contains corresponding `.txt` files with the same name as the images.

### 2. Label File Contents
Each `.txt` file contains one or more lines (one for each detected animal). A sample line looks like this:
`0 0.1367 0.2046 0.2734 0.4093`

**Breakdown of Values:**
| Value | Meaning | Description |
| :--- | :--- | :--- |
| `0` | **Class ID** | `0` is assigned to "Elephant" in our `data.yaml`. |
| `0.1367` | **X Center** | Horizontal center of the elephant (normalized 0-1). |
| `0.2046` | **Y Center** | Vertical center of the elephant (normalized 0-1). |
| `0.2734` | **Width** | Relative width of the bounding box. |
| `0.4093` | **Height** | Relative height of the bounding box. |

> [!NOTE]
> All coordinates are normalized (between 0 and 1). This allows the model to learn from images of any resolution or aspect ratio.

---

## Phase 6: Model Training Setup

We prepared the project for Amazon SageMaker fine-tuning of YOLOv11.

### 1. Training Scripts
- **`src/train_sagemaker.py`**: The script that runs inside the SageMaker container. It installs dependencies and starts the YOLOv11 training.
- **`scripts/launch_train.py`**: A local script to trigger the training job in AWS using the SageMaker Python SDK.

### 2. IAM Role for SageMaker
We created a dedicated service role to allow SageMaker to access S3 data and run compute tasks.

**Command:**
```powershell
# Create the role
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" iam create-role --role-name SageMakerExecutionRole --assume-role-policy-document file://c:/Users/saiki/Wildlife_detection_system/wildlife-detection-system/config/trust_policy.json

# Attach permissions
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" iam attach-role-policy --role-name SageMakerExecutionRole --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" iam attach-role-policy --role-name SageMakerExecutionRole --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

---

## Phase 7: Environment Setup

We created a Python virtual environment to isolate project dependencies and ensure compatibility.

### 1. Creating the Environment
A virtual environment (`venv`) was created using the base Python installation.

**Command:**
```powershell
python -m venv venv
```

### 2. Installing Dependencies
We installed all necessary libraries from `requirements.txt` into the virtual environment.

**Command:**
```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

> [!TIP]
> To activate the environment in your terminal, use:
> `.\venv\Scripts\Activate.ps1`

---

## Phase 8: Monitoring and Outputs

The SageMaker training job creates several artifacts in the AWS Cloud.

### 1. Trained Model Artifacts
When training finishes, the "brain" (weights) of your elephant detection model is saved to S3.
- **Location**: `s3://wildlife-detection-sau-186224145570/[job-name]/output/model.tar.gz`
- **What is it?**: A compressed file containing your best performing `.pt` weights.

### 2. Training Logs (Real-time)
You can watch the AI learn "live" in the cloud.
- **Service**: **Amazon CloudWatch**
- **How to view**:
  1. Open the [SageMaker Console](https://console.aws.amazon.com/sagemaker/).
  2. Go to **Training > Training jobs**.
  3. Click on your active job.
  4. Scroll to **Monitor** and click **View logs**.

---

## Phase 9: Model Deployment and Inference

Once training is complete, we move from "learning" to "doing."

### 1. Where does the model run?
We use **SageMaker Serverless Inference**. 
- **The Concept**: Instead of a server running 24/7, AWS only spins up the model for the few seconds it takes to analyze an image.
- **Cost**: You are only charged for the milliseconds the model is active. For a village alert system, this is the most affordable option.

### 2. What is the Output?
When the model "sees" an image, it returns **JSON data**. A sample output looks like this:

```json
[
  {
    "class": "elephant",
    "confidence": 0.94,
    "box": [120, 45, 300, 500]
  }
]
```

**Key Fields:**
| Field | Meaning |
| :--- | :--- |
| **`class`** | Confirms it found an "elephant". |
| **`confidence`** | How sure the AI is (e.g., 0.94 = 94% sure). |
| **`box`** | The pixel coordinates of the elephant in the photo. |

### 3. The "Brain" Connection
This JSON output is what our **Lambda Function** will read. If the confidence is high, the Lambda triggers the SNS alert to the village.

---

## Phase 10: The Alert System (SNS and DynamoDB)

We successfully initialized the "Voice" and "Memory" of our system.

### 1. Amazon SNS (Simple Notification Service)
We created a topic named `ElephantAlerts` which will act as our broadcast channel.

**Command:**
```powershell
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" sns create-topic --name ElephantAlerts --region us-east-1
```

### 2. Amazon DynamoDB
We created a table called `WildlifeDetections` to store our permanent logs.
- **Partition Key**: `DetectionId` (Unique ID for each alert)
- **Sort Key**: `Timestamp` (Allows us to see movement over time)

**Command:**
```powershell
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" dynamodb create-table --table-name WildlifeDetections --attribute-definitions AttributeName=DetectionId,AttributeType=S AttributeName=Timestamp,AttributeType=S --key-schema AttributeName=DetectionId,KeyType=HASH AttributeName=Timestamp,KeyType=RANGE --billing-mode PAY_PER_REQUEST --region us-east-1
```

### 3. Logic Handler (Lambda)
The core code is now ready in `src/lambda_handler.py`. It reads detections, saves them to the table, and triggers the SMS via SNS.

### 4. Email Subscription (Testing Channel)
1. **Lead Email**: saikiranvsns@gmail.com (Verified ✅)
2. **Secondary Email**: iamviswanadhveera@gmail.com (Awaiting Confirmation ⏳)

**Command to add more recipients:**
```powershell
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" sns subscribe --topic-arn arn:aws:sns:us-east-1:186224145570:ElephantAlerts --protocol email --notification-endpoint [EMAIL_ADDRESS] --region us-east-1
```

### 5. Testing the Flow
We created a test script `scripts/test_alert.py` to simulate an elephant detection and verify the integration between Lambda, DynamoDB, and SNS.

**Command:**
```powershell
.\venv\Scripts\python.exe scripts/test_alert.py
```

---


---

## Phase 12: SageMaker Notebook Training (Quota Workaround)

Due to delays in AWS Standard Training Quota approval, we implemented a workaround using an interactive **SageMaker Notebook Instance**.

### 1. Creating the Training Server
We launched a dedicated compute instance specifically for the fine-tuning process.
- **Instance Name**: `ElephantTrainingServer`
- **Type**: `ml.m5.xlarge`
- **Role**: `SageMakerExecutionRole`

**AWS CLI Command:**
```powershell
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" sagemaker create-notebook-instance --notebook-instance-name ElephantTrainingServer --instance-type ml.m5.xlarge --role-arn [ROLE_ARN] --region us-east-1
```

### 2. Interactive Training (JupyterLab Terminal)
Once the instance status is **InService**, we enter the server via the browser to start the AI learning.

**Step-by-Step Commands (Inside Jupyter Terminal):**
```bash
# A. Initialize project workspace
mkdir elephant_project && cd elephant_project
mkdir -p config

# B. Download the ROBUST Cloud Script (Version 2)
aws s3 cp s3://wildlife-detection-sau-186224145570/scripts/train_on_notebook_v2.py .

### 3. Execution Options

#### **Option A: Real-time (Screen Attached)**
Use this if you want to watch the logs live (must keep browser open).
```bash
python train_on_notebook_v2.py
```

#### **Option B: Unattended (Background)**
Use this if you want to turn off your PC while it trains (Safe for 15-20 hour runs).
```bash
nohup python train_on_notebook_v2.py > training_log.txt 2>&1 &
```
*To check progress later:* `tail -f training_log.txt`
- **Result**: Once "Training Complete!" appears, the model weights (`best.pt`) are saved locally on the instance.
- **Cleanup**: To save costs, the instance must be manually **Stopped** in the AWS Console immediately after the run.


---

## Phase 14: Resource & Cost Management

To ensure we stay within the **$200 AWS Credit Limit**, we carefully selected the `ml.m5.xlarge` instance type.

### 1. Cost Breakdown (`ml.m5.xlarge`)
- **Hourly Rate**: ~$0.23 per hour (us-east-1).
- **Estimated Duration**: 18 hours (for 10 epochs).
- **Total Estimated Cost**: **~$4.14 to $5.50**.

### 2. Credit Safety
Even with the overhead of S3 storage ($0.023/GB) and Lambda executions, the total training cost represents less than **3%** of your total credit budget.

### 3. Critical Shutdown Procedure
The most significant risk to the budget is leaving the server running after the training is complete.
1. Check the terminal for "Training Complete!".
2. Navigate to the **SageMaker Console**.
3. Select the instance -> **Actions** -> **Stop**.

---

## Phase 15: Monitoring Your AWS Bill & Credits

To see how much of your **$200 credit** you have used, follow these steps:

### 1. Open the Billing Console
- In the top search bar of the AWS Console, search for **"Billing"**.
- Click on **Billing and Cost Management**.

### 2. Check the "Home" Dashboard
- The main page will show you a "Month-to-date" summary of your current spending.
- **Note**: There is usually a **24-hour delay** in AWS billing updates. If you started training today, you might not see the cost until tomorrow morning.

### 3. Check Your Credits
- On the left sidebar, scroll down and find **"Credits"** (under the "Payments" or "Bills" section).
- Here you can see your **$200 balance** and exactly how much has been deducted so far.

### 4. Break Down Costs by Service
- Go to the **"Bills"** section on the left sidebar.
- You can expand the **SageMaker** or **S3** rows to see exactly how many hours of the `ml.m5.xlarge` instance you have been charged for.

---

## Phase 13: Summary of the Cloud Engine

The system is now fully configured in the Cloud. The camera lens is linked to S3, which triggers Lambda, which uses the SageMaker "Brain" to decide if an alert should be sent to the village via SNS.
