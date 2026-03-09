import json
import boto3
import uuid
from datetime import datetime

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
sns = boto3.client('sns', region_name='us-east-1')
table = dynamodb.Table('WildlifeDetections')
TOPIC_ARN = 'arn:aws:sns:us-east-1:186224145570:ElephantAlerts'

def lambda_handler(event, context):
    """
    Main entry point for detection alerts.
    Triggered when a new image is analyzed or uploaded.
    """
    # 1. Parse the detection results (mocking SageMaker output for now)
    detections = event.get('detections', [])
    image_uri = event.get('image_uri', 'unknown')
    
    elephant_spotted = False
    max_confidence = 0
    
    for det in detections:
        if det['class'] == 'elephant':
            elephant_spotted = True
            max_confidence = max(max_confidence, det['confidence'])

    # 2. If Elephant detected, Log and Alert
    if elephant_spotted:
        timestamp = datetime.now().isoformat()
        detection_id = str(uuid.uuid4())
        
        # Log to DynamoDB
        table.put_item(
            Item={
                'DetectionId': detection_id,
                'Timestamp': timestamp,
                'Animal': 'Elephant',
                'Confidence': str(max_confidence),
                'ImageURI': image_uri,
                'Status': 'ALERT_SENT'
            }
        )
        
        # Send SNS Alert
        message = f"🚨 ELEPHANT ALERT! 🚨\nAn elephant was detected with {max_confidence*100:.1f}% confidence.\nImage: {image_uri}\nTime: {timestamp}"
        
        sns.publish(
            TopicArn=TOPIC_ARN,
            Message=message,
            Subject="Wildlife Detection Alert"
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Alert sent and logged', 'id': detection_id})
        }

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'No elephants detected'})
    }
