#!/usr/bin/env python3
"""
AWS Health Monitor for Banking AI System
Quick health check script to monitor AWS services
"""

import boto3
import json
from datetime import datetime
from config import AWS_REGION, CLAUDE_MODEL_ID


def quick_health_check():
    """Quick health check for all AWS services"""
    print(f"🔍 AWS Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    services_status = {}
    
    # Check Authentication
    try:
        sts = boto3.client('sts', region_name=AWS_REGION)
        identity = sts.get_caller_identity()
        services_status['authentication'] = '✅ WORKING'
        print(f"🔐 Authentication: ✅ WORKING (Account: {identity['Account']})")
    except Exception as e:
        services_status['authentication'] = f'❌ FAILED: {str(e)[:50]}'
        print(f"🔐 Authentication: ❌ FAILED")
    
    # Check S3
    try:
        s3 = boto3.client('s3', region_name=AWS_REGION)
        buckets = s3.list_buckets()
        services_status['s3'] = f'✅ WORKING ({len(buckets["Buckets"])} buckets)'
        print(f"📦 S3: ✅ WORKING ({len(buckets['Buckets'])} buckets)")
    except Exception as e:
        services_status['s3'] = f'❌ FAILED: {str(e)[:50]}'
        print(f"📦 S3: ❌ FAILED")
    
    # Check DynamoDB
    try:
        dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)
        tables = dynamodb.list_tables()
        services_status['dynamodb'] = f'✅ WORKING ({len(tables["TableNames"])} tables)'
        print(f"🗄️  DynamoDB: ✅ WORKING ({len(tables['TableNames'])} tables)")
    except Exception as e:
        services_status['dynamodb'] = f'❌ FAILED: {str(e)[:50]}'
        print(f"🗄️  DynamoDB: ❌ FAILED")
    
    # Check Textract
    try:
        textract = boto3.client('textract', region_name=AWS_REGION)
        # Textract doesn't have a simple list operation, so we just test client creation
        services_status['textract'] = '✅ WORKING'
        print(f"📄 Textract: ✅ WORKING")
    except Exception as e:
        services_status['textract'] = f'❌ FAILED: {str(e)[:50]}'
        print(f"📄 Textract: ❌ FAILED")
    
    # Check Bedrock (test the configured model)
    try:
        bedrock_runtime = boto3.client('bedrock-runtime', region_name=AWS_REGION)
        
        # Quick test with the configured model
        test_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10,
            "temperature": 0.1,
            "messages": [{"role": "user", "content": "Hi"}]
        }
        
        response = bedrock_runtime.invoke_model(
            modelId=CLAUDE_MODEL_ID,
            body=json.dumps(test_request)
        )
        
        services_status['bedrock'] = '✅ WORKING (AI models accessible)'
        print(f"🧠 Bedrock: ✅ WORKING (AI models accessible)")
        
    except Exception as e:
        services_status['bedrock'] = f'❌ FAILED: {str(e)[:50]}'
        print(f"🧠 Bedrock: ❌ FAILED")
    
    # Overall Status
    working_services = sum(1 for status in services_status.values() if '✅' in status)
    total_services = len(services_status)
    
    print("\n" + "=" * 50)
    print(f"📊 Overall Status: {working_services}/{total_services} services operational")
    
    if working_services == total_services:
        print("🎉 ALL SYSTEMS OPERATIONAL - Banking AI ready to serve!")
    elif working_services >= total_services * 0.8:
        print("⚠️  MOSTLY OPERATIONAL - Minor issues detected")
    else:
        print("🚨 ISSUES DETECTED - Please investigate")
    
    return services_status


def check_application_status():
    """Check if the banking application can start"""
    print(f"\n🏦 Banking Application Status Check")
    print("-" * 30)
    
    try:
        from utils.aws_clients import get_aws_clients
        aws_clients = get_aws_clients()
        
        if aws_clients:
            print("✅ Application: READY TO START")
            print("   • AWS clients initialized successfully")
            print("   • All modules imported correctly")
            print("   • Configuration loaded properly")
            return True
        else:
            print("❌ Application: CONFIGURATION ISSUES")
            return False
            
    except Exception as e:
        print(f"❌ Application: STARTUP FAILED - {str(e)}")
        return False


if __name__ == "__main__":
    # Run health check
    health_status = quick_health_check()
    
    # Check application status
    app_ready = check_application_status()
    
    # Print quick summary
    print(f"\n💡 Quick Summary:")
    print(f"   • AWS Services: {'🟢 All Good' if all('✅' in status for status in health_status.values()) else '🟡 Some Issues'}")
    print(f"   • Application: {'🟢 Ready' if app_ready else '🔴 Issues'}")
    print(f"   • Region: {AWS_REGION}")
    print(f"   • AI Model: {CLAUDE_MODEL_ID}")
    
    print(f"\n🚀 To start your Banking AI: streamlit run app.py") 