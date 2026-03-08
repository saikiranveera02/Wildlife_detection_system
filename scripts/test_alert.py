import sys
import os

# Add src to path so we can import lambda_handler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from lambda_handler import lambda_handler

def test_flow():
    print("Starting End-to-End Test: Elephant Detection")
    
    # Mock event: Elephant spotted!
    mock_event = {
        "detections": [
            {"class": "elephant", "confidence": 0.98}
        ],
        "image_uri": "s3://wildlife-detection-sau-186224145570/uploads/test_elephant.jpg"
    }
    
    print("--- Sending Mock Event to Lambda ---")
    result = lambda_handler(mock_event, None)
    print(f"--- Lambda Output: {result['body']} ---")
    
    if result['statusCode'] == 200:
        print("\nSUCCESS: Check your email (saikiranvsns@gmail.com) for the alert!")
        print("SUCCESS: Check DynamoDB 'WildlifeDetections' table for the new log.")
    else:
        print("\nFAILED: Something went wrong.")

if __name__ == "__main__":
    test_flow()
