# Use official Ultralytics CPU-only image
FROM ultralytics/ultralytics:latest-cpu

# Set working directory
WORKDIR /app

# Set default AWS region for boto3
ENV AWS_DEFAULT_REGION=us-east-1

# Copy and install only extra dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn python-multipart boto3

# Copy the rest of the application
COPY src/ ./src/
COPY models/ ./models/

# Expose the API port
EXPOSE 8000

# Start the application
CMD ["python", "src/api.py"]
