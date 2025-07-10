#!/bin/bash

# Banking AI AWS Deployment Script
# This script deploys the Banking AI system to AWS App Runner

set -e

# Configuration
APP_NAME="banking-ai"
REGION="ap-south-1"
IAM_ROLE_NAME="BankingAI-AppRunner-Role"
IAM_POLICY_NAME="BankingAI-Policy"
S3_BUCKET_NAME="banking-ai-documents-$(date +%s)"

echo "🚀 Starting Banking AI Deployment to AWS..."
echo "================================================"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first:"
    echo "   https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI configured and credentials found"

# Step 1: Create IAM Policy
echo ""
echo "📋 Step 1: Creating IAM Policy..."
POLICY_ARN=$(aws iam create-policy \
    --policy-name $IAM_POLICY_NAME \
    --policy-document file://aws-iam-policy.json \
    --description "Policy for Banking AI system to access AWS services" \
    --query 'Policy.Arn' \
    --output text 2>/dev/null || echo "exists")

if [ "$POLICY_ARN" = "exists" ]; then
    echo "⚠️  Policy already exists, retrieving ARN..."
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/${IAM_POLICY_NAME}"
fi

echo "✅ IAM Policy created/found: $POLICY_ARN"

# Step 2: Create IAM Role for App Runner
echo ""
echo "👤 Step 2: Creating IAM Role for App Runner..."

# Create trust policy for App Runner
cat > trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "tasks.apprunner.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

# Create the role
aws iam create-role \
    --role-name $IAM_ROLE_NAME \
    --assume-role-policy-document file://trust-policy.json \
    --description "IAM role for Banking AI App Runner service" 2>/dev/null || echo "Role already exists"

# Attach the policy to the role
aws iam attach-role-policy \
    --role-name $IAM_ROLE_NAME \
    --policy-arn $POLICY_ARN

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $IAM_ROLE_NAME --query 'Role.Arn' --output text)
echo "✅ IAM Role created: $ROLE_ARN"

# Step 3: Create S3 Bucket for document storage
echo ""
echo "🗄️ Step 3: Creating S3 Bucket..."
aws s3 mb s3://$S3_BUCKET_NAME --region $REGION 2>/dev/null || echo "Bucket creation skipped (may already exist)"

# Configure bucket for private access
aws s3api put-bucket-encryption \
    --bucket $S3_BUCKET_NAME \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }
        ]
    }' 2>/dev/null || true

echo "✅ S3 Bucket created: s3://$S3_BUCKET_NAME"

# Step 4: Create DynamoDB Tables
echo ""
echo "🗃️ Step 4: Creating DynamoDB Tables..."

# Applications table
aws dynamodb create-table \
    --table-name banking-ai-applications \
    --attribute-definitions \
        AttributeName=application_id,AttributeType=S \
        AttributeName=timestamp,AttributeType=S \
    --key-schema \
        AttributeName=application_id,KeyType=HASH \
        AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION 2>/dev/null || echo "Applications table already exists"

# Agent memory table
aws dynamodb create-table \
    --table-name banking-ai-agent-memory \
    --attribute-definitions \
        AttributeName=agent_id,AttributeType=S \
        AttributeName=memory_id,AttributeType=S \
    --key-schema \
        AttributeName=agent_id,KeyType=HASH \
        AttributeName=memory_id,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION 2>/dev/null || echo "Agent memory table already exists"

echo "✅ DynamoDB Tables created"

# Step 5: Deploy to App Runner
echo ""
echo "🚀 Step 5: Deploying to AWS App Runner..."

# Create App Runner service configuration
cat > apprunner-service.json << EOF
{
    "ServiceName": "$APP_NAME",
    "SourceConfiguration": {
        "AutoDeploymentsEnabled": false,
        "CodeRepository": {
            "RepositoryUrl": "$(pwd)",
            "SourceCodeVersion": {
                "Type": "BRANCH",
                "Value": "main"
            },
            "CodeConfiguration": {
                "ConfigurationSource": "REPOSITORY",
                "CodeConfigurationValues": {
                    "Runtime": "DOCKER",
                    "BuildCommand": "docker build -t banking-ai .",
                    "StartCommand": "streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true",
                    "RuntimeEnvironmentVariables": {
                        "AWS_DEFAULT_REGION": "$REGION",
                        "AWS_REGION": "$REGION",
                        "S3_BUCKET_NAME": "$S3_BUCKET_NAME"
                    }
                }
            }
        }
    },
    "InstanceConfiguration": {
        "Cpu": "1 vCPU",
        "Memory": "2 GB",
        "InstanceRoleArn": "$ROLE_ARN"
    },
    "AutoScalingConfiguration": {
        "MinSize": 1,
        "MaxSize": 10,
        "MaxConcurrency": 100
    },
    "HealthCheckConfiguration": {
        "Protocol": "HTTP",
        "Path": "/_stcore/health",
        "IntervalSeconds": 30,
        "TimeoutSeconds": 5,
        "HealthyThresholdCount": 2,
        "UnhealthyThresholdCount": 5
    }
}
EOF

echo "⏳ Creating App Runner service (this may take 5-10 minutes)..."

# Note: App Runner doesn't support local directory deployment directly
# We'll provide instructions for manual deployment
echo ""
echo "📝 MANUAL DEPLOYMENT REQUIRED:"
echo "================================================================"
echo "AWS App Runner requires source code to be in a Git repository."
echo "Please follow these steps:"
echo ""
echo "1. Push your code to GitHub/GitLab/Bitbucket"
echo "2. Go to AWS Console > App Runner"
echo "3. Create a new service"
echo "4. Choose 'Source code repository'"
echo "5. Connect your repository"
echo "6. Use these configuration values:"
echo "   - Runtime: Docker"
echo "   - Build command: (leave empty, uses Dockerfile)"
echo "   - Start command: streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true"
echo "   - Port: 8501"
echo "   - Instance role: $IAM_ROLE_NAME"
echo "   - Environment variables:"
echo "     AWS_DEFAULT_REGION=$REGION"
echo "     AWS_REGION=$REGION"
echo "     S3_BUCKET_NAME=$S3_BUCKET_NAME"
echo ""

# Clean up temporary files
rm -f trust-policy.json apprunner-service.json

echo "✅ AWS resources created successfully!"
echo ""
echo "📊 DEPLOYMENT SUMMARY:"
echo "======================"
echo "• IAM Role: $IAM_ROLE_NAME"
echo "• IAM Policy: $IAM_POLICY_NAME" 
echo "• S3 Bucket: $S3_BUCKET_NAME"
echo "• DynamoDB Tables: banking-ai-applications, banking-ai-agent-memory"
echo "• Region: $REGION"
echo ""
echo "🔗 Next Steps:"
echo "1. Push your code to a Git repository"
echo "2. Follow the manual deployment steps above"
echo "3. Your app will be available at: https://[app-runner-url]"
echo ""
echo "🎉 Banking AI deployment setup complete!" 