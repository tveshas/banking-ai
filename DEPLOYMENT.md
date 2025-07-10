# 🚀 Banking AI - AWS EC2 Free Tier Deployment

This guide will help you deploy your Banking AI system to AWS EC2 using the **free tier**, keeping costs at $0/month for 12 months.

## 📋 Prerequisites

1. **AWS Account** (with free tier eligibility)
2. **AWS CLI** installed and configured
3. **SSH client** (Terminal on Mac/Linux, or PuTTY on Windows)

## ⚡ Quick Start (Automated Deployment)

### Option 1: Full Automated Deployment

```bash
# Make scripts executable
chmod +x ec2-deploy.sh upload-to-ec2.sh

# Run the full deployment script
./ec2-deploy.sh
```

This will:
- ✅ Create EC2 key pair
- ✅ Create security group with proper ports
- ✅ Create IAM role with required permissions  
- ✅ Launch t2.micro instance (free tier)
- ✅ Configure nginx reverse proxy
- ✅ Set up systemd service for auto-restart
- ✅ Create deployment package

## 📊 What You Get

### 🆓 Free Tier Resources
- **EC2 Instance**: t2.micro (1 vCPU, 1GB RAM)
- **Storage**: 30GB EBS (General Purpose SSD)
- **Data Transfer**: 1GB/month outbound
- **Duration**: 750 hours/month (always on for 12 months)

### 🏗️ Architecture
```
Internet → AWS Application Load Balancer → EC2 (t2.micro)
                                          ├── Nginx (Port 80)
                                          ├── Streamlit App (Port 8501)
                                          ├── Python 3.11
                                          └── Banking AI Agents
```

## 🔧 Manual Deployment Steps

### Step 1: Configure AWS CLI
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key  
# Default region: ap-south-1 (Mumbai)
# Default output format: json
```

### Step 2: Deploy Infrastructure
```bash
./ec2-deploy.sh
```

**Output will show:**
- 🔑 Key pair file: `banking-ai-key.pem`
- 🌐 Public IP address
- 📝 Instance ID

### Step 3: Upload Your Application
```bash
# Wait 2-3 minutes for instance to initialize, then:
./upload-to-ec2.sh <PUBLIC_IP> banking-ai-key.pem

# Example:
./upload-to-ec2.sh 13.232.123.45 banking-ai-key.pem
```

### Step 4: Access Your App
🌐 **Open in browser:** `http://<PUBLIC_IP>`

## 🔍 Troubleshooting

### Check Application Status
```bash
# SSH into your server
ssh -i banking-ai-key.pem ubuntu@<PUBLIC_IP>

# Check Banking AI service
sudo systemctl status banking-ai

# View real-time logs
sudo journalctl -u banking-ai -f

# Restart the application
sudo systemctl restart banking-ai
```

### Common Issues

#### 1. App not loading
```bash
# Check if service is running
sudo systemctl is-active banking-ai

# If not running, check logs
sudo journalctl -u banking-ai --no-pager -n 50
```

#### 2. Permission denied when uploading
```bash
# Fix key permissions
chmod 400 banking-ai-key.pem
```

#### 3. Port 80 not accessible
```bash
# Check security group allows HTTP (port 80)
aws ec2 describe-security-groups --group-names banking-ai-sg
```

## 📊 Monitoring & Costs

### Free Tier Monitoring
1. **AWS Console**: https://console.aws.amazon.com/billing/home#/freetier
2. **Set up billing alerts** for $1 threshold
3. **Monitor usage**: EC2, EBS, Data Transfer

### Expected Monthly Costs (After Free Tier)
- **t2.micro**: ~$8.50/month
- **30GB EBS**: ~$3.00/month
- **Data Transfer**: ~$0.09/GB
- **Total**: ~$12/month (very affordable!)

## 🔒 Security Best Practices

### 1. Secure SSH Access
```bash
# Restrict SSH to your IP only
YOUR_IP=$(curl -s https://checkip.amazonaws.com)
aws ec2 authorize-security-group-ingress \
    --group-name banking-ai-sg \
    --protocol tcp \
    --port 22 \
    --cidr $YOUR_IP/32
```

### 2. Enable HTTPS (Optional)
```bash
# SSH into server
ssh -i banking-ai-key.pem ubuntu@<PUBLIC_IP>

# Install Let's Encrypt certificate
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. Regular Updates
```bash
# Update system packages monthly
sudo apt update && sudo apt upgrade -y
```

## 🚀 Scaling & Production

### Upgrade to Production
1. **Change instance type**: t2.micro → t3.medium
2. **Add Application Load Balancer**
3. **Enable HTTPS** with SSL certificate
4. **Set up CloudWatch monitoring**
5. **Configure auto-scaling**

### Database Setup
```bash
# Create DynamoDB tables (free tier: 25GB)
aws dynamodb create-table \
    --table-name banking-ai-applications \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

## 📱 Testing Your Deployment

### 1. Basic Health Check
```bash
curl http://<PUBLIC_IP>/_stcore/health
# Should return: {"status": "ok"}
```

### 2. Upload Test Document
1. Open `http://<PUBLIC_IP>` in browser
2. Fill in customer details
3. Upload a test document (PNG/JPG/PDF)
4. Click "Start Autonomous AI Processing"
5. Verify AI agents process the application

### 3. Check AWS Services Integration
- **Bedrock**: AI model calls working
- **Textract**: Document processing
- **S3**: File storage (if configured)

## 🆘 Support & Cleanup

### Get Help
- **Logs**: `sudo journalctl -u banking-ai -f`
- **System**: `sudo systemctl status banking-ai`
- **Nginx**: `sudo nginx -t && sudo systemctl status nginx`

### Cleanup Resources (To Stop Charges)
```bash
# Get instance ID
aws ec2 describe-instances --filters "Name=tag:Name,Values=banking-ai-server" \
    --query 'Reservations[*].Instances[*].InstanceId' --output text

# Terminate instance
aws ec2 terminate-instances --instance-ids <INSTANCE_ID>

# Delete key pair
aws ec2 delete-key-pair --key-name banking-ai-key

# Delete security group (after instance terminates)
aws ec2 delete-security-group --group-name banking-ai-sg
```

## 🎉 Success!

Your Banking AI system is now running on AWS EC2 free tier!

- 🌐 **Access**: `http://<PUBLIC_IP>`
- 💰 **Cost**: $0/month (free tier)
- 🔧 **Management**: SSH access with full control
- 📈 **Scalable**: Easy to upgrade when needed

---

**💡 Pro Tip**: Set up a Route 53 domain ($12/year) to get a nice URL like `bankingai.yourdomain.com` instead of IP addresses! 