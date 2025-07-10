"""
AWS clients utility for the Banking AI System
"""

import boto3
from config import AWS_REGION

def get_aws_clients():
    try:
        return {
            'textract': boto3.client('textract', region_name=AWS_REGION),
            'bedrock': boto3.client('bedrock-runtime', region_name=AWS_REGION),
            'bedrock_runtime': boto3.client('bedrock-runtime', region_name=AWS_REGION),
            's3': boto3.client('s3', region_name=AWS_REGION),
            'dynamodb': boto3.resource('dynamodb', region_name=AWS_REGION)
        }
    except Exception as e:
        print(f"AWS client initialization failed: {e}")
        return None 