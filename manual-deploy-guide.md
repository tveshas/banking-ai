# 🖱️ Manual AWS Console Deployment Guide

Since your AWS user has limited permissions, let's deploy using the AWS Console - it's actually easier and gives you more control!

## 🚀 Step-by-Step Manual Deployment

### Step 1: Launch EC2 Instance

1. **Go to EC2 Console**: https://console.aws.amazon.com/ec2/
2. **Click "Launch Instance"**
3. **Configure the instance:**

```
Name: banking-ai-server
Application and OS Images: Ubuntu Server 22.04 LTS (Free tier eligible)
Instance type: t2.micro (Free tier eligible)
Key pair: Create new key pair
   - Name: banking-ai-key
   - Type: RSA
   - Format: .pem
   - Download and save the .pem file!
```

### Step 2: Configure Security Group

In the "Network settings" section:
```
☑️ Allow SSH traffic from: My IP
☑️ Allow HTTP traffic from the internet  
☑️ Allow HTTPS traffic from the internet
```

**Add custom rule for Streamlit:**
- Type: Custom TCP
- Port: 8501
- Source: 0.0.0.0/0 (Anywhere)

### Step 3: Advanced Details (Important!)

Scroll down to "Advanced details" and paste this in **User data**:

```bash
#!/bin/bash
set -e

# Update system
apt-get update -y
apt-get upgrade -y

# Install Python 3.11 and dependencies
apt-get install -y python3.11 python3.11-pip python3.11-venv
apt-get install -y nginx git curl unzip

# Create app user
useradd -m -s /bin/bash bankingai
mkdir -p /home/bankingai/app
chown -R bankingai:bankingai /home/bankingai

# Setup application environment
sudo -u bankingai bash << 'USEREOF'
cd /home/bankingai/app

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
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

# Configure nginx
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

echo "✅ EC2 setup completed!" > /var/log/setup.log
```

### Step 4: Launch Instance

Click **"Launch instance"** and wait 2-3 minutes for it to boot.

### Step 5: Get Your Public IP

1. Go to **EC2 → Instances**
2. Select your `banking-ai-server` instance
3. Copy the **Public IPv4 address** (something like `13.232.123.45`)

## 📦 Upload Your Application

Now let's get your Banking AI code onto the server:

### Method 1: Create Deployment Package Locally

```bash
# In your local aws folder, create the package
tar -czf banking-ai-app.tar.gz \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pem' \
    --exclude='*.tar.gz' \
    *.py agents/ models/ utils/ requirements.txt
```

### Method 2: Upload to Server

```bash
# Replace YOUR_PUBLIC_IP with actual IP and path to your .pem file
chmod 400 ~/Downloads/banking-ai-key.pem
scp -i ~/Downloads/banking-ai-key.pem banking-ai-app.tar.gz ubuntu@YOUR_PUBLIC_IP:~/
```

### Method 3: Setup on Server

```bash
# SSH into your server
ssh -i ~/Downloads/banking-ai-key.pem ubuntu@YOUR_PUBLIC_IP

# Extract and setup the application
sudo tar -xzf banking-ai-app.tar.gz -C /home/bankingai/app/
sudo chown -R bankingai:bankingai /home/bankingai/app/

# Install dependencies and start service
sudo -u bankingai bash -c "
cd /home/bankingai/app
source venv/bin/activate
pip install --no-cache-dir -r requirements.txt
"

# Start the Banking AI service
sudo systemctl restart banking-ai
sudo systemctl enable banking-ai

# Check if it's running
sudo systemctl status banking-ai
```

## 🎉 Test Your Deployment

1. **Open browser**: `http://YOUR_PUBLIC_IP`
2. **You should see**: Banking AI interface with empty form fields
3. **Test the enhanced features**:
   - Enter address: "Gurgaon, 122018" 
   - It should now correctly classify as **Urban** (not Rural!)
   - Upload a test document and process

## 🔧 Troubleshooting

### If app isn't loading:
```bash
# Check service status
sudo systemctl status banking-ai

# View logs
sudo journalctl -u banking-ai -f

# Restart if needed
sudo systemctl restart banking-ai
```

### If nginx isn't working:
```bash
# Check nginx
sudo systemctl status nginx
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

## 🔒 Add AWS Permissions (Optional)

If you want to use Bedrock/Textract, you'll need to add IAM permissions:

1. **Go to IAM Console**: https://console.aws.amazon.com/iam/
2. **Roles → Create role**
3. **Service: EC2**
4. **Attach policies:**
   - `AmazonBedrockFullAccess`
   - `AmazonTextractFullAccess`
   - `AmazonS3FullAccess`
5. **Name the role**: `BankingAI-EC2-Role`
6. **Go back to EC2 → Your instance → Actions → Security → Modify IAM role**
7. **Select your new role**

## 💰 Cost Monitoring

- **Free for 12 months**: t2.micro instance
- **Monitor usage**: AWS Console → Billing → Free Tier
- **Set billing alert**: $1 threshold recommended

---

**🎯 Result**: Your Banking AI will be live at `http://YOUR_PUBLIC_IP` with all the fixes we implemented (proper pincode classification, asyncio handling, etc.)! 