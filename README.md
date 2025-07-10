# 🏦 Banking AI - Autonomous Document Processing & Risk Assessment System

An advanced AI-powered banking system that automates document processing, risk assessment, and customer segmentation using AWS services and multi-agent architecture.

## 🌐 Live Demo

- **🚀 Live Application**: [http://15.206.211.200/](http://15.206.211.200/)
- **📹 Demo Video**: [https://youtu.be/JwrBqmt0R6w](https://youtu.be/JwrBqmt0R6w)

## 🚀 Features

### 🤖 Multi-Agent Architecture
- **Document Agent**: Autonomous document processing with AWS Textract
- **Risk Agent**: Intelligent customer risk assessment and scoring
- **Orchestrator**: Coordinated multi-agent workflow management

### 📄 Document Processing
- **Automated OCR**: Extract text from banking documents using AWS Textract
- **Smart Analysis**: AI-powered document understanding and data extraction
- **Multi-format Support**: PDF, images, and various document formats
- **Real-time Processing**: Instant document analysis and insights

### 🎯 Risk Assessment
- **Customer Profiling**: Comprehensive risk scoring based on multiple factors
- **Segmentation**: Advanced urban/rural classification with regional intelligence
- **Predictive Analytics**: AI-driven risk prediction models
- **Compliance Integration**: Built-in regulatory compliance checks

### 🌍 Geographic Intelligence
- **Enhanced Pincode Classification**: Accurate urban/rural detection
- **Regional Optimization**: Specialized for Indian banking (Mumbai region)
- **Smart City Recognition**: Intelligent classification for areas like Gurgaon (122xxx)
- **Location-based Risk Factors**: Geographic risk assessment integration

### 💻 User Interface
- **Streamlit Dashboard**: Modern, responsive web interface
- **Real-time Updates**: Live processing status and results
- **Form Management**: Clean, empty forms ready for data entry
- **Interactive Visualizations**: Charts and graphs for data insights

## 🏗️ Architecture

### AWS Services Integration
- **Amazon Bedrock**: Advanced AI/ML model integration
- **Amazon Textract**: Document text extraction and analysis
- **Amazon S3**: Secure document storage and management
- **Amazon DynamoDB**: High-performance data storage
- **AWS IAM**: Secure access and permission management

### Technical Stack
- **Backend**: Python 3.12 with asyncio support
- **Frontend**: Streamlit web framework
- **AI/ML**: AWS Bedrock with Claude models
- **Database**: DynamoDB for scalable data storage
- **Storage**: S3 for document management
- **Infrastructure**: EC2 with nginx reverse proxy

## 📋 Prerequisites

### AWS Requirements
- AWS Account with active credentials
- IAM permissions for Bedrock, Textract, S3, DynamoDB
- AWS CLI configured for Mumbai region (ap-south-1)

### System Requirements
- Python 3.12+
- pip package manager
- Git for version control
- Modern web browser

## 🚀 Quick Start

### Local Development
```bash
# Clone the repository
git clone <repository-url>
cd banking-ai

# Install dependencies
pip install -r requirements.txt

# Set up AWS credentials
aws configure

# Run the application
streamlit run app.py
```

### Production Deployment
```bash
# Deploy to EC2 (Ubuntu 24.04)
chmod +x quick-upload.sh
./quick-upload.sh <EC2-IP> <path-to-key.pem>
```

## 📝 Configuration

### Environment Variables
```bash
# AWS Configuration
export AWS_REGION=ap-south-1
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key

# Application Settings
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### AWS Services Setup
1. **Bedrock**: Enable Claude models in Mumbai region
2. **Textract**: Activate document analysis APIs
3. **S3**: Create bucket for document storage
4. **DynamoDB**: Set up tables for data persistence

## 🔧 Key Components

### Core Agents (`agents/`)
- `document_agent.py` - Document processing and analysis
- `risk_agent.py` - Customer risk assessment
- `orchestrator.py` - Multi-agent coordination

### Models (`models/`)
- `base_agent.py` - Base agent architecture
- `data_models.py` - Data structures and schemas

### Utilities (`utils/`)
- `aws_clients.py` - AWS service integration
- `customer_segmentation.py` - Geographic classification
- `ui_components.py` - Streamlit UI elements

### Configuration
- `config.py` - Application configuration and AWS setup
- `app.py` - Main Streamlit application
- `main.py` - Core application logic

## 🛡️ Security Features

### Rate Limiting Protection
- **Exponential Backoff**: Intelligent retry mechanisms
- **Throttling Handling**: AWS API rate limit management
- **Progressive Delays**: Adaptive delay strategies

### Error Handling
- **Async Loop Management**: RuntimeError prevention
- **Safe JSON Parsing**: Robust data processing
- **Exception Handling**: Comprehensive error recovery

### Data Security
- **AWS IAM Integration**: Secure access control
- **Encrypted Storage**: S3 encryption at rest
- **Secure Transmission**: HTTPS/TLS for all communications

## 🌐 Deployment Options

### Local Development
```bash
streamlit run app.py
# Access: http://localhost:8501
```

### AWS EC2 Production
- **Instance Type**: t2.micro (free tier compatible)
- **OS**: Ubuntu 24.04 LTS
- **Services**: Streamlit + Nginx reverse proxy
- **Auto-restart**: Systemd service management

### Container Deployment
```bash
# Build Docker image
docker build -t banking-ai .

# Run container
docker run -p 8501:8501 banking-ai
```

## 📊 Performance Features

### Optimization
- **Async Processing**: Non-blocking operations
- **Caching**: Intelligent data caching strategies
- **Connection Pooling**: Efficient AWS service connections
- **Memory Management**: Optimized resource usage

### Monitoring
- **Health Checks**: Application health monitoring
- **Performance Metrics**: Response time tracking
- **Error Logging**: Comprehensive error tracking
- **AWS CloudWatch**: Integrated monitoring

## 🧪 Testing

### Test Files
- `test_mumbai_models.py` - Model testing for Mumbai region
- `mumbai_region_test.py` - Regional functionality tests

### Test Coverage
- ✅ Document processing workflows
- ✅ Risk assessment algorithms
- ✅ AWS service integration
- ✅ Error handling mechanisms
- ✅ Geographic classification accuracy

## 📖 API Documentation

### Core Functions
```python
# Document processing
process_document(file_path) -> DocumentResult

# Risk assessment
assess_customer_risk(customer_data) -> RiskScore

# Geographic classification
classify_location(pincode) -> LocationType
```

### Agent Communication
- **Message Passing**: Inter-agent communication
- **State Management**: Shared state coordination
- **Event Handling**: Asynchronous event processing

## 🚀 Recent Enhancements

### v2.0 Features
- ✅ **Enhanced Pincode Classification**: Improved Gurgaon detection
- ✅ **Empty Form Management**: Clean data entry forms
- ✅ **Rate Limiting Protection**: AWS throttling handling
- ✅ **Async Loop Fixes**: RuntimeError resolution
- ✅ **Production Deployment**: Complete EC2 setup

### Bug Fixes
- Fixed asyncio RuntimeError in nested loops
- Resolved AWS Bedrock throttling issues
- Enhanced customer segmentation accuracy
- Improved form field management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues
- **AWS Credentials**: Ensure proper IAM permissions
- **Rate Limits**: Check AWS service quotas
- **Memory Issues**: Monitor EC2 instance resources
- **Network**: Verify security group settings

### Contact
- **Issues**: Use GitHub Issues for bug reports
- **Questions**: Create GitHub Discussions
- **Security**: Email security concerns privately

## 🏆 Acknowledgments

- AWS for comprehensive cloud services
- Streamlit for the excellent web framework
- OpenAI/Anthropic for AI model capabilities
- The open-source community for various tools and libraries

---

**🏦 Banking AI - Revolutionizing Financial Document Processing with AI** 🚀 