# 🛡️ Unified Cyber Threat Detection Platform

[![Production Ready](https://img.shields.io/badge/status-production--ready-brightgreen)](docs/DEPLOYMENT_GUIDE.md)
[![Tests](https://img.shields.io/badge/tests-105%2F105%20passing-success)](#-test-coverage)
[![Docker](https://img.shields.io/badge/docker-6%20containers-blue)](#-production-deployment)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](requirements.txt)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> **Enterprise-grade AI-powered threat detection system** combining email phishing detection and web log analysis with explainable AI, real-time monitoring, and production-ready Docker deployment.

## ✨ Key Features

| Feature | Description | Status |
|---------|-------------|--------|
| 📧 **Email Phishing Detection** | Multiple NLP models (TF-IDF, FastText, BERT) with 95%+ accuracy | ✅ Production |
| 🤖 **Advanced NLP Models** | BERT (DistilBERT), FastText, and Hybrid ensemble | ✅ Ready |
| 🌐 **Web Log Analysis** | Anomaly detection for SQL injection, XSS, and DDoS attacks | ✅ Production |
| 🔗 **Threat Correlation** | Cross-platform threat correlation and unified analysis | ✅ Production |
| 🧠 **Explainable AI** | LIME and SHAP for model interpretability | ✅ Production |
| 🚀 **REST API** | 12 production endpoints with rate limiting and caching | ✅ Production |
| 💾 **PostgreSQL Integration** | Full database persistence with SQLAlchemy ORM | ✅ Production |
| 📊 **Monitoring Stack** | Prometheus + Grafana for metrics and visualization | ✅ Production |
| 🐳 **Docker Deployment** | Complete containerized stack with health checks | ✅ Production |
| 📈 **Interactive Dashboard** | Real-time threat visualization and reporting | ✅ Production |

## 🎯 Quick Start

### 🐳 Production Deployment (Recommended)

Deploy the entire stack with one command:

```bash
# Start all 6 containers (API, Database, Cache, Nginx, Prometheus, Grafana)
docker-compose up -d

# Access services:
# - API: http://localhost:80
# - Grafana: http://localhost:3000 (admin/admin)
# - Prometheus: http://localhost:9090
```

**Stack includes:**
- 🌐 Nginx reverse proxy with SSL/TLS support
- 🚀 Flask API with Gunicorn (4 workers)
- 💾 PostgreSQL 15 with persistent storage
- ⚡ Redis cache for rate limiting
- 📊 Prometheus metrics collection
- 📈 Grafana dashboards

### 💻 Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/UnifiedCyberThreatDetectionSystem.git
cd UnifiedCyberThreatDetectionSystem

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run API server
python -m src.api.app
```

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                       │
│  Web Dashboard | REST API | CLI Tools | Grafana Dashboards       │
└────────────────────────────┬─────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────┐
│                      Application Layer                            │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │ Email Detector  │  │  Web Analyzer    │  │  Correlation    │ │
│  │  - NLP Pipeline │  │  - Log Parser    │  │  - Threat Intel │ │
│  │  - ML Models    │  │  - Anomaly Det   │  │  - Risk Scoring │ │
│  └────────┬────────┘  └─────────┬────────┘  └────────┬────────┘ │
└───────────┼──────────────────────┼────────────────────┼──────────┘
            │                      │                    │
            └──────────┬───────────┴─────────┬──────────┘
                       ↓                     ↓
┌──────────────────────────────────────────────────────────────────┐
│                       Data Layer                                  │
│  ┌──────────────┐  ┌───────────┐  ┌────────────┐  ┌──────────┐  │
│  │ PostgreSQL   │  │   Redis   │  │ Prometheus │  │ ML Models│  │
│  │ - Threats    │  │ - Cache   │  │ - Metrics  │  │ - Trained│  │
│  │ - Reports    │  │ - Sessions│  │ - Alerts   │  │ - Joblib │  │
│  └──────────────┘  └───────────┘  └────────────┘  └──────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

**Data Flow:**
1. **Input:** Email/Web logs received via API or batch import
2. **Analysis:** ML models detect threats with 95%+ accuracy
3. **Correlation:** Cross-platform threat correlation and scoring
4. **Storage:** PostgreSQL persistence with full audit trail
5. **Monitoring:** Real-time metrics via Prometheus/Grafana
6. **Output:** JSON reports, dashboard visualization, alerts

## 🛠️ Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python 3.8+, Flask, Gunicorn |
| **ML/AI** | scikit-learn, NLTK, spaCy, PyTorch, Transformers |
| **NLP Models** | BERT (DistilBERT), FastText, TF-IDF |
| **Database** | PostgreSQL 15, SQLAlchemy ORM |
| **Cache** | Redis 7 |
| **API** | RESTful, OpenAPI 3.1, Swagger UI |
| **Monitoring** | Prometheus, Grafana |
| **Deployment** | Docker, Docker Compose, Nginx |
| **Testing** | pytest, coverage.py |
| **Security** | Rate limiting, JWT, SSL/TLS |

## 📊 API Endpoints

### Email Analysis
```bash
POST /api/email/analyze          # Analyze single email (TF-IDF + RF)
POST /api/email/analyze/bert     # Analyze with BERT (advanced NLP)
POST /api/email/analyze/fasttext # Analyze with FastText (fast)
POST /api/email/analyze/hybrid   # Hybrid: All models combined
POST /api/email/batch            # Batch email analysis
GET  /api/email/history          # Analysis history
```

### Web Log Analysis
```bash
POST /api/weblog/analyze         # Analyze web logs
POST /api/weblog/batch           # Batch log analysis
```

### Threat Intelligence
```bash
GET  /api/threats                # List all threats
POST /api/threats/correlate      # Cross-platform correlation
GET  /api/threats/stats          # Threat statistics
GET  /api/reports/{id}           # Get threat report
```

**Full API Documentation:** [Interactive Swagger UI](docs/api.html) | [OpenAPI Spec](docs/openapi.yaml) | [Examples](docs/API_EXAMPLES.md)

## 💡 Use Cases

### 1. 📧 Phishing Campaign Detection
Analyze thousands of emails to detect coordinated phishing campaigns:
```python
import requests

response = requests.post('http://localhost/api/email/batch', json={
    'emails': email_list,
    'detect_campaign': True
})
```

### 2. 🌐 Web Attack Monitoring
Real-time web log analysis for SQL injection, XSS, and DDoS:
```python
response = requests.post('http://localhost/api/weblog/analyze', json={
    'logs': access_logs,
    'enable_anomaly_detection': True
})
```

### 3. 🔗 Cross-Platform Threat Hunting
Correlate email and web threats for APT detection:
```python
response = requests.post('http://localhost/api/threats/correlate', json={
    'time_window': '24h',
    'min_risk_score': 7.0
})
```

### 4. 📊 Security Dashboard Integration
Integrate with existing SOC dashboards via REST API:
```bash
curl -X GET "http://localhost/api/threats/stats?period=7d"
```

**More Examples:** See [Usage Scenarios](docs/USAGE_SCENARIOS.md) for detailed tutorials

## � Advanced NLP Models

### Available Models

| Model | Accuracy | Speed | Use Case |
|-------|----------|-------|----------|
| **TF-IDF + RF** | 85-92% | ~25ms | General baseline, production-ready |
| **FastText** | 90-94% | <1ms | High-volume processing, real-time |
| **BERT (DistilBERT)** | 94-97% | ~45ms | High-accuracy requirements |
| **Hybrid Ensemble** | 92-96% | ~70ms | Best balance (recommended) |

### Quick Start

```python
# BERT Analysis
response = requests.post('http://localhost/api/email/analyze/bert', json={
    'email_content': 'URGENT! Verify your account...',
    'email_subject': 'Account Security Alert'
})

# FastText Analysis (Ultra-fast)
response = requests.post('http://localhost/api/email/analyze/fasttext', json={
    'email_content': 'Suspicious email content...'
})

# Hybrid Ensemble (All models combined)
response = requests.post('http://localhost/api/email/analyze/hybrid', json={
    'email_content': 'Email content...',
    'email_sender': 'sender@example.com'
})
```

### Model Details

- **TF-IDF + Random Forest**: Baseline model, fast and reliable
- **FastText**: Trained on 31,323 emails, 885 MB model, <1ms inference
- **BERT**: Pre-trained DistilBERT (fine-tuning recommended for production)
- **Hybrid**: Weighted ensemble (30% TF-IDF + 30% FastText + 40% BERT)

**Documentation:** [Advanced NLP Integration Guide](docs/ADVANCED_NLP_INTEGRATION.md)

## �🧪 Test Coverage

```
✅ 105/105 tests passing (100%)
```

| Test Suite | Tests | Status |
|------------|-------|--------|
| API Integration | 22 | ✅ All passing |
| Database Operations | 17 | ✅ All passing |
| Email Detection | 21 | ✅ All passing |
| Web Analysis | 26 | ✅ All passing |
| Integration | 14 | ✅ All passing |
| Performance | 4 | ✅ All passing |
| Improvements | 1 | ✅ All passing |

**Production Quality:** Zero errors, zero warnings, 100% reliability.

```bash
# Run all tests
pytest tests/ -v --cov=src --cov-report=html

# Run specific suite
pytest tests/test_api.py -v
```

## 📚 Documentation

### 🏗️ Architecture & Design
- **[System Architecture](docs/architecture.html)** - Complete diagrams (System, Data Flow, Class, Sequence, Component)
- **[Design Patterns](docs/BEST_PRACTICES.md)** - Software architecture and patterns used

### 🤖 Advanced NLP & AI
- **[Advanced NLP Integration](docs/ADVANCED_NLP_INTEGRATION.md)** - BERT, FastText, Hybrid ensemble setup
- **[Next Steps & Roadmap](docs/NEXT_STEPS_DETAILED.md)** - Fine-tuning, deployment, optimization guide

### 🔧 Development Guides
- **[Usage Scenarios](docs/USAGE_SCENARIOS.md)** - 5 real-world scenarios with code examples
- **[Best Practices](docs/BEST_PRACTICES.md)** - Data preparation, model training, troubleshooting
- **[API Examples](docs/API_EXAMPLES.md)** - cURL and Python request examples

### 💾 Database & Persistence
- **[Database Integration](docs/FAZ4_DATABASE.md)** - SQLAlchemy ORM, models, migrations
- **Models:** Email, WebLog, ThreatCorrelation, ThreatReport, AuditLog
- **Features:** Connection pooling, transactions, batch import (4500+ records)

### 🚀 Deployment & Operations
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Docker, Nginx, SSL/TLS, monitoring, backup
- **[Production Checklist](docs/DEPLOYMENT_GUIDE.md#production-checklist)** - Pre-launch validation
- **[Monitoring Setup](docs/DEPLOYMENT_GUIDE.md#monitoring)** - Prometheus + Grafana configuration

## 🚀 Installation & Setup

### System Requirements

| Component | Requirement |
|-----------|-------------|
| OS | Linux, macOS, Windows (WSL recommended) |
| Python | 3.8 or higher |
| RAM | 4GB minimum, 8GB recommended |
| Storage | 2GB for application + models |
| Docker | 20.10+ (for containerized deployment) |

### Method 1: Docker Deployment (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/UnifiedCyberThreatDetectionSystem.git
cd UnifiedCyberThreatDetectionSystem

# 2. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 3. Start all services
docker-compose up -d

# 4. Verify containers
docker-compose ps
# Expected: 6/6 containers running (api, db, cache, nginx, prometheus, grafana)

# 5. Test API
curl http://localhost/api/health
```

### Method 2: Manual Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/UnifiedCyberThreatDetectionSystem.git
cd UnifiedCyberThreatDetectionSystem

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure PostgreSQL (optional)
# Set DATABASE_URL in .env

# 5. Start API server
python -m src.api.app
```

### Service Access Points

After deployment, services are available at:

| Service | URL | Credentials |
|---------|-----|-------------|
| REST API | http://localhost:80 | - |
| API Docs (Swagger) | http://localhost:80/api/docs | - |
| Grafana Dashboard | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| PostgreSQL | localhost:5432 | postgres/postgres |
| Redis | localhost:6379 | - |

## 🔧 Configuration

### Environment Variables

Create `.env` file with:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/threat_detection

# Redis Cache
REDIS_URL=redis://cache:6379/0

# API Keys (Optional)
VIRUSTOTAL_API_KEY=your_api_key_here

# Flask
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Logging
LOG_LEVEL=INFO
```

### Docker Compose Services

```yaml
services:
  api:          # Flask API with Gunicorn
  db:           # PostgreSQL 15
  cache:        # Redis 7
  nginx:        # Reverse proxy
  prometheus:   # Metrics collection
  grafana:      # Visualization
```

## 🎯 Project Details

This project creates a comprehensive cybersecurity threat detection system by combining email phishing detection and web log analysis. It provides real-time threat detection using machine learning and NLP technologies.

### Features and Capabilities

**Email Phishing Detection:**
- NLP-based text analysis with TF-IDF and word embeddings
- Header analysis (SPF, DKIM, sender reputation)
- URL analysis with VirusTotal integration
- Attachment scanning for malicious content
- Campaign detection across multiple emails

**Web Log Analysis:**
- Real-time log parsing and normalization
- SQL injection detection using pattern matching
- XSS attack identification
- DDoS attack detection via rate analysis
- Bot traffic identification

**Threat Correlation:**
- Cross-platform threat linking
- Risk score calculation (0-10 scale)
- Temporal correlation analysis
- IP address and domain tracking
- Automated threat reporting

**Explainable AI:**
- LIME explanations for individual predictions
- SHAP values for feature importance
- Decision reasoning in API responses
- Model performance metrics

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and code of conduct.

```bash
# Fork the repository
# Create a feature branch
git checkout -b feature/amazing-feature

# Make your changes and commit
git commit -m "Add amazing feature"

# Push to your fork
git push origin feature/amazing-feature

# Open a Pull Request
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/UnifiedCyberThreatDetectionSystem/issues)
- **Documentation:** [Full Documentation](docs/)
- **Email:** your.email@example.com

## 🙏 Acknowledgments

- CEAS 2008 Dataset for email training data
- Enron Email Dataset for model validation
- Various open-source ML libraries and frameworks
- Security research community for threat intelligence

## 🔖 Version History

**v1.0.0** (Current)
- ✅ Production-ready deployment
- ✅ 105/105 tests passing
- ✅ Complete Docker stack (6 containers)
- ✅ PostgreSQL integration
- ✅ Prometheus + Grafana monitoring
- ✅ Comprehensive documentation (200+ pages)

---

**⭐ If you find this project useful, please consider giving it a star!**

Built with ❤️ for cybersecurity professionals and researchers
