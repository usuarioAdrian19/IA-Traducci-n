import boto3
import os
from dotenv import load_dotenv

load_dotenv()

region = os.environ.get("REGION")
ak = os.environ.get("ACCESS_KEY_ID")
sk = os.environ.get("ACCESS_SECRET_KEY")

rekognition_client = boto3.client(
    'rekognition',
    region_name=region,
    aws_access_key_id=ak,
    aws_secret_access_key=sk
)

def detect_text_in_image(bucket_name, image_name):
    response = rekognition_client.detect_text(
        Image={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': image_name
            }
        }
    )
    return response
