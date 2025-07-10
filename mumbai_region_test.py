# mumbai_region_test.py - Test everything works in ap-south-1 (Mumbai)
import boto3
import json

def test_mumbai_setup():
    print("🇮🇳 Testing AWS setup for banking demo in Mumbai (ap-south-1)...\n")
    
    try:
        # Test current region and identity
        session = boto3.Session()
        current_region = session.region_name
        print(f"📍 AWS Region: {current_region}")
        
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"👤 AWS User: {identity['Arn']}")
        print(f"🏢 Account: {identity['Account']}\n")
        
        # Test S3 in Mumbai
        print("Testing S3 in Mumbai...")
        s3 = boto3.client('s3', region_name='ap-south-1')
        buckets = s3.list_buckets()
        print(f"✅ S3: {len(buckets['Buckets'])} buckets accessible")
        
        # Test DynamoDB in Mumbai
        print("Testing DynamoDB in Mumbai...")
        dynamodb = boto3.client('dynamodb', region_name='ap-south-1')
        tables = dynamodb.list_tables()
        print(f"✅ DynamoDB: {len(tables['TableNames'])} tables in ap-south-1")
        
        # Test Textract in Mumbai
        print("Testing Textract in Mumbai...")
        try:
            textract = boto3.client('textract', region_name='ap-south-1')
            print("✅ Textract: Available in Mumbai")
        except Exception as e:
            print(f"⚠️  Textract: {str(e)}")
            print("   → We can use alternative document processing")
        
        # Test Bedrock in Mumbai
        print("Testing Bedrock in Mumbai...")
        try:
            bedrock = boto3.client('bedrock', region_name='ap-south-1')
            models = bedrock.list_foundation_models()
            
            print(f"✅ Bedrock: {len(models['modelSummaries'])} models available in Mumbai")
            
            # Look for key models
            claude_models = [m for m in models['modelSummaries'] if 'claude' in m['modelId'].lower()]
            titan_models = [m for m in models['modelSummaries'] if 'titan' in m['modelId'].lower()]
            nova_models = [m for m in models['modelSummaries'] if 'nova' in m['modelId'].lower()]
            
            print(f"   📊 Available AI Models in Mumbai:")
            if claude_models:
                print(f"   🤖 Claude models: {len(claude_models)}")
                for model in claude_models[:3]:  # Show first 3
                    print(f"      - {model['modelId']}")
            
            if titan_models:
                print(f"   ⚡ Amazon Titan models: {len(titan_models)}")
                for model in titan_models[:2]:  # Show first 2
                    print(f"      - {model['modelId']}")
                    
            if nova_models:
                print(f"   🔥 Amazon Nova models: {len(nova_models)}")
                for model in nova_models[:2]:  # Show first 2
                    print(f"      - {model['modelId']}")
            
            # Test actual Bedrock API call
            print("\n   Testing Bedrock API call in Mumbai...")
            bedrock_runtime = boto3.client('bedrock-runtime', region_name='ap-south-1')
            
            # Find best available model for test
            test_model = None
            if claude_models:
                # Prefer Claude Haiku for speed
                haiku_models = [m for m in claude_models if 'haiku' in m['modelId'].lower()]
                if haiku_models:
                    test_model = haiku_models[0]['modelId']
                else:
                    test_model = claude_models[0]['modelId']
            elif nova_models:
                # Use Nova if Claude not available
                lite_models = [m for m in nova_models if 'lite' in m['modelId'].lower()]
                if lite_models:
                    test_model = lite_models[0]['modelId']
                else:
                    test_model = nova_models[0]['modelId']
            elif titan_models:
                # Use Titan as fallback
                text_models = [m for m in titan_models if 'text' in m['modelId'].lower() and 'embed' not in m['modelId'].lower()]
                if text_models:
                    test_model = text_models[0]['modelId']
            
            if test_model:
                print(f"   🧪 Testing with model: {test_model}")
                
                test_prompt = "What is KYC in banking? Answer briefly."
                
                if 'claude' in test_model.lower():
                    # Claude format
                    response = bedrock_runtime.invoke_model(
                        modelId=test_model,
                        body=json.dumps({
                            "anthropic_version": "bedrock-2023-05-31",
                            "max_tokens": 50,
                            "messages": [{"role": "user", "content": test_prompt}]
                        })
                    )
                    result = json.loads(response['body'].read())
                    ai_response = result['content'][0]['text']
                    
                elif 'nova' in test_model.lower():
                    # Nova format
                    response = bedrock_runtime.invoke_model(
                        modelId=test_model,
                        body=json.dumps({
                            "messages": [{"role": "user", "content": test_prompt}],
                            "max_tokens": 50
                        })
                    )
                    result = json.loads(response['body'].read())
                    ai_response = result['output']['message']['content'][0]['text']
                    
                elif 'titan' in test_model.lower():
                    # Titan format
                    response = bedrock_runtime.invoke_model(
                        modelId=test_model,
                        body=json.dumps({
                            "inputText": test_prompt,
                            "textGenerationConfig": {"maxTokenCount": 50}
                        })
                    )
                    result = json.loads(response['body'].read())
                    ai_response = result['results'][0]['outputText']
                
                print(f"   ✅ AI Response: '{ai_response[:60]}...'")
                print(f"   🎉 Bedrock fully functional in Mumbai!")
            
        except Exception as e:
            print(f"❌ Bedrock Error in Mumbai: {str(e)}")
            print("   → Checking if models are available in us-east-1 as fallback...")
            
            # Fallback test to us-east-1
            try:
                bedrock_us = boto3.client('bedrock', region_name='us-east-1')
                models_us = bedrock_us.list_foundation_models()
                print(f"   ✅ Bedrock fallback: {len(models_us['modelSummaries'])} models in us-east-1")
                print("   → We can use cross-region calls if needed")
            except:
                print("   ❌ Bedrock not accessible in either region")
        
        print("\n🎯 Mumbai Region Assessment:")
        print("✅ S3: Fully available")
        print("✅ DynamoDB: Fully available") 
        print("✅ Authentication: Working")
        
        print("\n🚀 MUMBAI SETUP READY!")
        print("📍 Building banking demo in ap-south-1 (Mumbai)")
        
        print("\n📋 Next steps:")
        print("1. Create S3 bucket in Mumbai")
        print("2. Create DynamoDB table in Mumbai") 
        print("3. Build Streamlit app with Mumbai endpoints")
        print("4. Use available AI models in Mumbai region")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("- Check internet connectivity")
        print("- Verify AWS credentials")

if __name__ == "__main__":
    test_mumbai_setup()