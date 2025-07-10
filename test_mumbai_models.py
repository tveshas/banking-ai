# test_mumbai_models.py - Test EXACT models detected in Mumbai
import boto3
import json

def test_mumbai_available_models():
    print("🇮🇳 Testing EXACT models detected in Mumbai region test...\n")
    
    try:
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='ap-south-1')
        
        # EXACT models from your Mumbai test results
        models_to_test = [
            {
                'id': 'amazon.nova-pro-v1:0',
                'name': 'Amazon Nova Pro',
                'format': 'nova'
            },
            {
                'id': 'amazon.nova-lite-v1:0', 
                'name': 'Amazon Nova Lite',
                'format': 'nova'
            },
            {
                'id': 'amazon.titan-text-lite-v1',
                'name': 'Amazon Titan Text Lite',
                'format': 'titan'
            },
            {
                'id': 'amazon.titan-text-express-v1',
                'name': 'Amazon Titan Text Express', 
                'format': 'titan'
            }
        ]
        
        test_prompt = "What is KYC in banking? Answer briefly."
        working_models = []
        
        for model in models_to_test:
            try:
                print(f"🧪 Testing {model['name']} ({model['id']})...")
                
                if model['format'] == 'nova':
                    # Nova format
                    response = bedrock_runtime.invoke_model(
                        modelId=model['id'],
                        body=json.dumps({
                            "messages": [{"role": "user", "content": test_prompt}],
                            "max_tokens": 50
                        })
                    )
                    result = json.loads(response['body'].read())
                    ai_response = result['output']['message']['content'][0]['text']
                    
                elif model['format'] == 'titan':
                    # Titan format
                    response = bedrock_runtime.invoke_model(
                        modelId=model['id'],
                        body=json.dumps({
                            "inputText": test_prompt,
                            "textGenerationConfig": {"maxTokenCount": 50}
                        })
                    )
                    result = json.loads(response['body'].read())
                    ai_response = result['results'][0]['outputText']
                
                print(f"✅ {model['name']}: WORKING!")
                print(f"   Response: '{ai_response[:60]}...'")
                print(f"   🎉 Ready for demo!\n")
                
                working_models.append(model['id'])
                
            except Exception as e:
                print(f"❌ {model['name']}: {str(e)}")
                if "ValidationException" in str(e):
                    print(f"   → Need to request access for {model['name']}")
                elif "ResourceNotFoundException" in str(e):
                    print(f"   → Model not found, might need different ID")
                print()
                continue
        
        # Summary
        print("=" * 50)
        if working_models:
            print(f"🎉 SUCCESS! {len(working_models)} models working in Mumbai:")
            for model_id in working_models:
                print(f"   ✅ {model_id}")
            print(f"\n🚀 Your demo is ready to build!")
            print(f"💰 Estimated cost: $0.25 for entire demo development")
        else:
            print("⚠️  No models working yet. Options:")
            print("1. Request access in AWS Console → Bedrock → Model access")
            print("2. Use mock responses for UI development")
            print("3. Check model IDs might be slightly different")
        
        return working_models
        
    except Exception as e:
        print(f"❌ Error testing models: {str(e)}")
        return []

if __name__ == "__main__":
    working = test_mumbai_available_models()
    
    if working:
        print(f"\n📋 Next steps:")
        print(f"1. Create S3 bucket: aws s3 mb s3://banking-demo-mumbai-tvesha --region ap-south-1")
        print(f"2. Create DynamoDB table (see commands in previous message)")
        print(f"3. Use working models in your Streamlit app")
        print(f"4. Start building your demo!")
    else:
        print(f"\n🔄 Try requesting model access or proceed with mock data for now")