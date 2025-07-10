#!/bin/bash

# Quick Banking AI Upload Script
# Usage: ./quick-upload.sh PUBLIC_IP PATH_TO_PEM_FILE

set -e

if [ $# -ne 2 ]; then
    echo "🚀 Quick Banking AI Upload"
    echo "=========================="
    echo ""
    echo "Usage: $0 <PUBLIC_IP> <PEM_FILE_PATH>"
    echo ""
    echo "Example:"
    echo "  $0 13.232.123.45 ~/Downloads/banking-ai-key.pem"
    echo ""
    echo "Steps to get these:"
    echo "1. Go to EC2 Console and launch instance using manual-deploy-guide.md"
    echo "2. Get Public IP from EC2 instance details"
    echo "3. Download the .pem key file when creating the instance"
    echo ""
    exit 1
fi

PUBLIC_IP=$1
PEM_FILE=$2

echo "🚀 Quick Banking AI Upload"
echo "=========================="
echo "Target: $PUBLIC_IP"
echo "Key: $PEM_FILE"
echo ""

# Check if PEM file exists
if [ ! -f "$PEM_FILE" ]; then
    echo "❌ PEM file not found: $PEM_FILE"
    echo "Make sure you downloaded the key pair when creating the EC2 instance"
    exit 1
fi

# Check if deployment package exists
if [ ! -f "banking-ai-app.tar.gz" ]; then
    echo "📦 Creating deployment package..."
    tar -czf banking-ai-app.tar.gz \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='.git' \
        --exclude='*.pem' \
        --exclude='*.tar.gz' \
        --exclude='*.log' \
        *.py agents/ models/ utils/ requirements.txt
    echo "✅ Package created!"
fi

# Set correct permissions
chmod 400 "$PEM_FILE"

echo ""
echo "⬆️  Uploading Banking AI..."
scp -i "$PEM_FILE" -o StrictHostKeyChecking=no banking-ai-app.tar.gz ubuntu@$PUBLIC_IP:~/

echo ""
echo "🔧 Setting up on server..."
ssh -i "$PEM_FILE" -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP << 'EOF'
echo "Extracting application..."
sudo tar -xzf banking-ai-app.tar.gz -C /home/bankingai/app/
sudo chown -R bankingai:bankingai /home/bankingai/app/

echo "Installing dependencies..."
sudo -u bankingai bash -c "
cd /home/bankingai/app
source venv/bin/activate
pip install --no-cache-dir -r requirements.txt
"

echo "Starting Banking AI service..."
sudo systemctl restart banking-ai
sudo systemctl enable banking-ai

echo "Waiting for service to start..."
sleep 10

if sudo systemctl is-active --quiet banking-ai; then
    echo "✅ Banking AI is running!"
else
    echo "❌ Service failed. Checking logs..."
    sudo journalctl -u banking-ai --no-pager -n 10
fi

if sudo systemctl is-active --quiet nginx; then
    echo "✅ Nginx is running!"
else
    echo "🔄 Starting nginx..."
    sudo systemctl start nginx
    sudo systemctl enable nginx
fi
EOF

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================"
echo ""
echo "🌐 Your Banking AI is now live at:"
echo "   http://$PUBLIC_IP"
echo ""
echo "🧪 Test the enhanced features:"
echo "   • Enter address: 'Gurgaon, 122018'"
echo "   • Should classify as Urban (not Rural)"
echo "   • Upload test documents"
echo ""
echo "🔧 Useful commands:"
echo "   SSH: ssh -i $PEM_FILE ubuntu@$PUBLIC_IP"
echo "   Logs: sudo journalctl -u banking-ai -f"
echo "   Restart: sudo systemctl restart banking-ai"
echo "" 