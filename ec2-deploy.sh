#!/bin/bash

# Banking AI EC2 Free Tier Deployment Script
# This script creates and configures an EC2 free tier instance for the Banking AI system

set -e

# Configuration
INSTANCE_NAME="banking-ai-server"
REGION="ap-south-1"
INSTANCE_TYPE="t2.micro"  # Free tier eligible
AMI_ID="ami-0e742cca61fb65051"  # Ubuntu 22.04 LTS for ap-south-1
KEY_NAME="banking-ai-key"
SECURITY_GROUP_NAME="banking-ai-sg"
IAM_ROLE_NAME="BankingAI-EC2-Role"
IAM_POLICY_NAME="BankingAI-Policy"

echo "🚀 Starting Banking AI EC2 Free Tier Deployment..."
echo "=================================================="

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI configured and credentials found"

# Step 1: Create Key Pair
echo ""
echo "🔑 Step 1: Creating EC2 Key Pair..."
if ! aws ec2 describe-key-pairs --key-names $KEY_NAME &> /dev/null; then
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --query 'KeyMaterial' \
        --output text > ${KEY_NAME}.pem
    chmod 400 ${KEY_NAME}.pem
    echo "✅ Key pair created: ${KEY_NAME}.pem"
else
    echo "⚠️  Key pair already exists: $KEY_NAME"
fi

# Step 2: Create Security Group
echo ""
echo "🛡️ Step 2: Creating Security Group..."
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text)

if ! aws ec2 describe-security-groups --group-names $SECURITY_GROUP_NAME &> /dev/null; then
    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name $SECURITY_GROUP_NAME \
        --description "Security group for Banking AI application" \
        --vpc-id $VPC_ID \
        --query 'GroupId' \
        --output text)
    
    # Allow SSH (port 22)
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0
    
    # Allow HTTP (port 80)
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0
    
    # Allow HTTPS (port 443)
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0
    
    # Allow Streamlit (port 8501)
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 8501 \
        --cidr 0.0.0.0/0
    
    echo "✅ Security group created: $SECURITY_GROUP_ID"
else
    SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --group-names $SECURITY_GROUP_NAME --query 'SecurityGroups[0].GroupId' --output text)
    echo "⚠️  Security group already exists: $SECURITY_GROUP_ID"
fi

# Step 3: Create IAM Role and Policy
echo ""
echo "👤 Step 3: Creating IAM Role..."

# Create IAM policy for EC2 instance
aws iam create-policy \
    --policy-name $IAM_POLICY_NAME \
    --policy-document file://aws-iam-policy.json \
    --description "Policy for Banking AI system to access AWS services" &> /dev/null || echo "Policy already exists"

# Get policy ARN
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/${IAM_POLICY_NAME}"

# Create trust policy for EC2
cat > ec2-trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

# Create IAM role
aws iam create-role \
    --role-name $IAM_ROLE_NAME \
    --assume-role-policy-document file://ec2-trust-policy.json \
    --description "IAM role for Banking AI EC2 instance" &> /dev/null || echo "Role already exists"

# Attach policy to role
aws iam attach-role-policy \
    --role-name $IAM_ROLE_NAME \
    --policy-arn $POLICY_ARN

# Create instance profile
aws iam create-instance-profile \
    --instance-profile-name $IAM_ROLE_NAME &> /dev/null || echo "Instance profile already exists"

# Add role to instance profile
aws iam add-role-to-instance-profile \
    --instance-profile-name $IAM_ROLE_NAME \
    --role-name $IAM_ROLE_NAME &> /dev/null || echo "Role already in instance profile"

echo "✅ IAM Role created: $IAM_ROLE_NAME"

# Step 4: Create user data script
echo ""
echo "📝 Step 4: Creating user data script..."
cat > user-data.sh << 'EOF'
#!/bin/bash
set -e

# Update system
apt-get update -y
apt-get upgrade -y

# Install Python 3.11 and pip
apt-get install -y python3.11 python3.11-pip python3.11-venv
apt-get install -y nginx git curl unzip

# Create app user
useradd -m -s /bin/bash bankingai
mkdir -p /home/bankingai/app
chown -R bankingai:bankingai /home/bankingai

# Clone or setup application (placeholder - you'll need to upload your code)
sudo -u bankingai bash << 'USEREOF'
cd /home/bankingai/app

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install pip packages (placeholder requirements)
cat > requirements.txt << 'REQEOF'
streamlit>=1.28.0
boto3>=1.28.0
pandas>=2.0.0
nest_asyncio>=1.5.0
asyncio>=3.4.3
dataclasses>=0.6
typing-extensions>=4.0.0
python-dateutil>=2.8.0
REQEOF

pip install --no-cache-dir -r requirements.txt
USEREOF

# Create systemd service
cat > /etc/systemd/system/banking-ai.service << 'SERVICEEOF'
[Unit]
Description=Banking AI Streamlit Application
After=network.target

[Service]
Type=simple
User=bankingai
WorkingDirectory=/home/bankingai/app
Environment=PATH=/home/bankingai/app/venv/bin
Environment=PYTHONPATH=/home/bankingai/app
ExecStart=/home/bankingai/app/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true --server.fileWatcherType=none --browser.gatherUsageStats=false
Restart=always

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Configure nginx as reverse proxy
cat > /etc/nginx/sites-available/banking-ai << 'NGINXEOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
NGINXEOF

# Enable nginx site
ln -sf /etc/nginx/sites-available/banking-ai /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Start services
systemctl enable nginx
systemctl start nginx
systemctl enable banking-ai

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install
rm -rf awscliv2.zip aws

# Set up log rotation
cat > /etc/logrotate.d/banking-ai << 'LOGEOF'
/var/log/banking-ai/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 bankingai bankingai
    postrotate
        systemctl reload banking-ai
    endscript
}
LOGEOF

mkdir -p /var/log/banking-ai
chown bankingai:bankingai /var/log/banking-ai

echo "✅ EC2 instance setup completed!" > /var/log/ec2-setup.log
EOF

# Step 5: Launch EC2 Instance
echo ""
echo "🚀 Step 5: Launching EC2 Instance..."

INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --count 1 \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SECURITY_GROUP_ID \
    --iam-instance-profile Name=$IAM_ROLE_NAME \
    --user-data file://user-data.sh \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "✅ EC2 Instance launched: $INSTANCE_ID"
echo "⏳ Waiting for instance to be running..."

aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "✅ Instance is running!"

# Step 6: Create deployment package
echo ""
echo "📦 Step 6: Creating deployment package..."
tar -czf banking-ai-app.tar.gz \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pem' \
    --exclude='*.tar.gz' \
    *.py agents/ models/ utils/ requirements.txt

echo "✅ Deployment package created: banking-ai-app.tar.gz"

# Clean up temporary files
rm -f ec2-trust-policy.json user-data.sh

echo ""
echo "🎉 EC2 FREE TIER DEPLOYMENT COMPLETE!"
echo "====================================="
echo ""
echo "📊 DEPLOYMENT SUMMARY:"
echo "• Instance ID: $INSTANCE_ID"
echo "• Public IP: $PUBLIC_IP"
echo "• Instance Type: $INSTANCE_TYPE (Free Tier)"
echo "• Security Group: $SECURITY_GROUP_ID"
echo "• Key Pair: ${KEY_NAME}.pem"
echo "• IAM Role: $IAM_ROLE_NAME"
echo ""
echo "🔗 NEXT STEPS:"
echo "1. Wait 2-3 minutes for the instance to fully initialize"
echo "2. Upload your code:"
echo "   scp -i ${KEY_NAME}.pem banking-ai-app.tar.gz ubuntu@${PUBLIC_IP}:~/"
echo "   ssh -i ${KEY_NAME}.pem ubuntu@${PUBLIC_IP}"
echo "   sudo tar -xzf banking-ai-app.tar.gz -C /home/bankingai/app/"
echo "   sudo chown -R bankingai:bankingai /home/bankingai/app/"
echo "   sudo systemctl start banking-ai"
echo ""
echo "3. Access your app:"
echo "   🌐 http://${PUBLIC_IP}"
echo "   🔒 SSH: ssh -i ${KEY_NAME}.pem ubuntu@${PUBLIC_IP}"
echo ""
echo "💰 FREE TIER INFO:"
echo "• 750 hours/month of t2.micro (always free for 12 months)"
echo "• Monitor usage at: https://console.aws.amazon.com/billing/home#/freetier"
echo ""
echo "🔧 TROUBLESHOOTING:"
echo "• Check logs: sudo journalctl -u banking-ai -f"
echo "• Restart app: sudo systemctl restart banking-ai"
echo "• Check nginx: sudo systemctl status nginx" 