# Use Python 3.9 slim image
FROM python:3.9-slim

# Install system dependencies for OpenCV and YOLO
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY src/ ./src/
COPY models/ ./models/

# Expose the API port
EXPOSE 8000

# Start the application
CMD ["python", "src/api.py"]
