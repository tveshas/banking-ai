#!/bin/bash

# Simple upload script for Banking AI to EC2
# Use this if you already have an EC2 instance running

set -e

# Check if required parameters are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <ec2-public-ip> <key-file.pem>"
    echo "Example: $0 13.232.123.45 banking-ai-key.pem"
    exit 1
fi

EC2_IP=$1
KEY_FILE=$2

echo "🚀 Uploading Banking AI to EC2..."
echo "================================="
echo "EC2 IP: $EC2_IP"
echo "Key File: $KEY_FILE"

# Check if key file exists
if [ ! -f "$KEY_FILE" ]; then
    echo "❌ Key file $KEY_FILE not found!"
    exit 1
fi

# Set correct permissions for key file
chmod 400 $KEY_FILE

echo ""
echo "📦 Creating deployment package..."
tar -czf banking-ai-app.tar.gz \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pem' \
    --exclude='*.tar.gz' \
    --exclude='*.log' \
    *.py agents/ models/ utils/ requirements.txt

echo "✅ Package created: banking-ai-app.tar.gz"

echo ""
echo "⬆️ Uploading to EC2..."
scp -i $KEY_FILE banking-ai-app.tar.gz ubuntu@$EC2_IP:~/

echo ""
echo "🔧 Setting up application on EC2..."
ssh -i $KEY_FILE ubuntu@$EC2_IP << 'EOF'
# Extract application
sudo tar -xzf banking-ai-app.tar.gz -C /home/bankingai/app/
sudo chown -R bankingai:bankingai /home/bankingai/app/

# Install dependencies
sudo -u bankingai bash -c "
cd /home/bankingai/app
source venv/bin/activate
pip install --no-cache-dir -r requirements.txt
"

# Restart the application
sudo systemctl restart banking-ai
sudo systemctl enable banking-ai

# Check status
sleep 5
if sudo systemctl is-active --quiet banking-ai; then
    echo "✅ Banking AI service is running!"
else
    echo "❌ Banking AI service failed to start. Check logs:"
    sudo journalctl -u banking-ai --no-pager -n 20
fi

# Check nginx
if sudo systemctl is-active --quiet nginx; then
    echo "✅ Nginx is running!"
else
    echo "⚠️ Nginx is not running. Starting..."
    sudo systemctl start nginx
    sudo systemctl enable nginx
fi

echo ""
echo "🔍 Service Status:"
sudo systemctl status banking-ai --no-pager -l
EOF

# Clean up local package
rm -f banking-ai-app.tar.gz

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================"
echo ""
echo "🌐 Your Banking AI app is now available at:"
echo "   http://$EC2_IP"
echo ""
echo "🔧 Useful commands:"
echo "   SSH: ssh -i $KEY_FILE ubuntu@$EC2_IP"
echo "   Check logs: sudo journalctl -u banking-ai -f"
echo "   Restart app: sudo systemctl restart banking-ai"
echo "   Check status: sudo systemctl status banking-ai"
echo ""
echo "📱 Test your app by visiting: http://$EC2_IP" 