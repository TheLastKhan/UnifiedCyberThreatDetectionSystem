# 🛡️ CyberGuard - Unified Cyber Threat Detection System
## AŞAMA 4.5 + 6 Completion Guide

---

## 📊 Project Status

### Completed Phases
- ✅ AŞAMA 4.3: Data Quality Analysis & Cleaning
- ✅ AŞAMA 4.4: Model Training (Random Forest + Isolation Forest)
- ✅ AŞAMA 4.5: Model Optimization (Ensemble Methods)
- ✅ AŞAMA 6: Frontend Enhancement (Modern Dashboard + REST API)

### Model Performance Summary

#### Email Phishing Detection
| Model | Accuracy | F1-Score | ROC-AUC | Status |
|-------|----------|----------|---------|--------|
| **Stacking Ensemble** | 89.60% | **86.18%** | **96.65%** | 🏆 BEST |
| Voting Ensemble | 88.48% | 84.28% | 96.39% | Excellent |
| Random Forest (Tuned) | 85.82% | 78.59% | 95.48% | Good |

#### Web Anomaly Detection
- **Model**: Isolation Forest
- **Features**: 8 (request_length, SQL/XSS patterns, URL analysis, etc.)
- **Contamination**: 0.1 (10% anomalies)
- **Training**: 1,200 synthetic samples (1000 normal, 200 anomalies)

---

## 🚀 Getting Started

### 1. Prerequisites
```bash
# Python 3.10+
python --version

# Install dependencies
pip install -r requirements.txt

# Verify venv is active
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
```

### 2. Run Dashboard Server
```bash
# Start Flask web server
python run_dashboard.py

# Server will start on:
# http://localhost:5000
```

### 3. Access Web Interface
```
Open browser: http://localhost:5000
```

---

## 📡 REST API Endpoints

### Health Check
```bash
GET /api/health

Response:
{
  "status": "healthy",
  "timestamp": "2025-12-09T15:24:11.935Z",
  "version": "1.0.0"
}
```

### Email Analysis
```bash
POST /api/email/analyze

Request:
{
  "subject": "Email subject",
  "body": "Email content...",
  "sender": "sender@example.com"
}

Response:
{
  "is_phishing": boolean,
  "model_confidence": {
    "phishing_probability": 0.87,
    "legitimate_probability": 0.13,
    "model_type": "ensemble (stacking + voting)",
    "prediction": "phishing"
  },
  "features": {...},
  "timestamp": "2025-12-09T15:24:11.935Z"
}
```

### Web Log Analysis
```bash
POST /api/web/analyze

Request:
{
  "ip": "203.0.113.45",
  "method": "POST",
  "path": "/admin/login",
  "status": "401",
  "user_agent": "sqlmap/1.0"
}

Response:
{
  "is_anomalous": boolean,
  "model_analysis": {
    "is_anomalous": true,
    "anomaly_score": -0.5847,
    "model_type": "isolation_forest",
    "features_used": 8,
    "contamination": 0.1
  },
  "timestamp": "2025-12-09T15:24:11.935Z"
}
```

### Batch Email Analysis
```bash
POST /api/email/batch

Request:
{
  "emails": [
    {"subject": "...", "body": "...", "sender": "..."},
    ...
  ]
}

Response:
{
  "count": 2,
  "results": [...],
  "timestamp": "2025-12-09T15:24:11.935Z"
}
```

### Batch Web Log Analysis
```bash
POST /api/web/batch

Request:
{
  "logs": [
    {"ip": "...", "method": "...", "path": "..."},
    ...
  ]
}

Response:
{
  "total_logs": 3,
  "anomalous_count": 1,
  "anomaly_rate": 33.33,
  "results": [...],
  "timestamp": "2025-12-09T15:24:11.935Z"
}
```

### Model Status
```bash
GET /api/models/status

Response:
{
  "stacking_model": true,
  "voting_model": true,
  "tfidf_vectorizer": true,
  "web_anomaly_detector": true,
  "web_scaler": true,
  "timestamp": "2025-12-09T15:24:11.935Z"
}
```

### Reload Models
```bash
POST /api/models/reload

Response:
{
  "success": true,
  "timestamp": "2025-12-09T15:24:11.935Z"
}
```

---

## 🎨 Dashboard Features

### Pages
1. **Dashboard**: System status, metrics, threat distribution chart, recent alerts
2. **Email Analysis**: Analyze individual emails, real-time phishing detection
3. **Web Analysis**: Analyze HTTP logs, anomaly detection
4. **Reports**: Daily summary, model performance metrics
5. **Settings**: Dark mode, language, model threshold, notifications

### Key Features
- ✅ Dark Mode (toggle in sidebar)
- ✅ Real-time system status
- ✅ Model performance visualization (Chart.js)
- ✅ Responsive design (mobile-friendly)
- ✅ Keyboard shortcuts navigation
- ✅ Settings persistence (localStorage)

---

## 🧪 Testing

### Run API Tests
```bash
# Start server first:
python run_dashboard.py

# In another terminal:
python test_api.py

# Test cases:
# 1. Health check
# 2. Email analysis (phishing detection)
# 3. Web log analysis (anomaly detection)
# 4. Model status check
# 5. Batch email analysis
```

### Manual Testing with curl
```bash
# Health check
curl http://localhost:5000/api/health

# Analyze email
curl -X POST http://localhost:5000/api/email/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Urgent: Verify Your Account",
    "body": "Click here: http://malicious.fake/verify",
    "sender": "fake@scam.com"
  }'

# Analyze web log
curl -X POST http://localhost:5000/api/web/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "203.0.113.45",
    "method": "POST",
    "path": "/admin/login",
    "status": "401",
    "user_agent": "sqlmap/1.0"
  }'
```

---

## 📁 Project Structure

```
UnifiedCyberThreatDetectionSystem/
├── models/                          # Trained ML models
│   ├── email_detector_stacking.pkl  # Best email model
│   ├── email_detector_voting.pkl    # Voting ensemble
│   ├── email_detector_rf_tuned.pkl  # Tuned random forest
│   ├── tfidf_vectorizer.pkl         # TF-IDF vectorizer
│   ├── web_anomaly_detector.pkl     # Isolation forest
│   └── log_scaler.pkl               # Feature scaler
│
├── web_dashboard/
│   ├── api.py                       # REST API blueprint (400+ lines)
│   ├── app.py                       # Flask main app
│   ├── static/
│   │   ├── css/styles.css          # Modern dashboard styles
│   │   └── js/script.js            # Dashboard interactions
│   └── templates/
│       └── dashboard.html           # Dashboard UI (500+ lines)
│
├── src/
│   ├── email_detector/
│   │   ├── detector.py
│   │   ├── features.py
│   │   └── utils.py
│   ├── web_analyzer/
│   │   ├── analyzer.py
│   │   ├── patterns.py
│   │   └── utils.py
│   └── unified_platform/
│       ├── platform.py
│       ├── correlation.py
│       └── reporting.py
│
├── notebooks/                       # Jupyter analysis notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_email_analysis.ipynb
│   ├── 03_web_log_analysis.ipynb
│   └── 04_unified_analysis.ipynb
│
├── data/
│   ├── processed/                   # Cleaned datasets
│   ├── raw/                         # Original datasets
│   └── samples/                     # Sample data
│
├── train_email_model.py             # Email model training
├── train_web_anomaly_model.py       # Web model training
├── optimize_models.py               # Hyperparameter optimization
├── run_dashboard.py                 # Start web server
├── test_api.py                      # API test suite
├── requirements.txt                 # Python dependencies
└── README.md                        # Project documentation
```

---

## 🔧 Configuration

### Environment Variables (.env)
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Flask
FLASK_ENV=development
FLASK_DEBUG=True

# API Keys (optional)
VIRUSTOTAL_API_KEY=your_key_here
KAGGLE_API_TOKEN=your_token_here
```

---

## 📈 Model Training Details

### Training Data
- **Source**: 18 CSV datasets (280,943 rows)
- **Email**: 263,057 email texts (30,420 legitimate, 19,609 phishing/spam)
- **Web**: Synthetic + demo logs (1,200 samples)

### Feature Engineering
**Email**:
- TF-IDF Vectorization (5000 features, 1-2 grams)
- Text normalization (lowercase, stemming)
- Bigram analysis for better context

**Web**:
- Request length analysis
- SQL injection pattern detection
- XSS pattern detection
- URL length and complexity
- Query parameter analysis
- Special character ratio
- Uppercase character ratio

### Hyperparameter Tuning (GridSearchCV)
- **Parameters Tested**: 24 combinations
- **Cross Validation**: 3-fold
- **Best Params**: max_depth=25, min_samples_leaf=1, min_samples_split=3, n_estimators=100

---

## 🎯 Next Steps / Future Enhancements

1. **AŞAMA 7**: Production Deployment
   - Docker containerization
   - Kubernetes orchestration
   - CI/CD pipeline setup

2. **AŞAMA 8**: Advanced Features
   - Real-time threat intelligence feeds
   - Machine learning model updates
   - User management system
   - Advanced reporting

3. **AŞAMA 9**: Security Hardening
   - OAuth2/JWT authentication
   - SSL/TLS configuration
   - Rate limiting
   - DDoS protection

---

## 📝 Git Commits

```
7a87a9e - AŞAMA 4.5 + 6: Model Optimization + Dashboard
7290aa8 - AŞAMA 4.4: Model Training Complete
69feb5f - AŞAMA 4.3: Data Quality Analysis & Cleaning
35275c1 - Fix SQLAlchemy enum import for 2.0+
```

---

## 🆘 Troubleshooting

### Models not loading
```bash
# Check models directory
ls models/
# Should contain: *.pkl files

# Reload models via API
curl -X POST http://localhost:5000/api/models/reload
```

### Dashboard not responding
```bash
# Check Flask server
# Windows: 
python -c "import flask; print(flask.__version__)"

# Restart server
python run_dashboard.py
```

### API timeout
```bash
# Check model size and memory
# Increase timeout in api.py if needed
# Default: 5 minutes for GridSearchCV
```

---

## 📧 Contact & Support

For issues or questions:
1. Check logs in `reports/` directory
2. Review error messages in Flask console
3. Consult notebooks for model analysis
4. Check API test results

---

## 📄 License

This project is part of the Unified Cyber Threat Detection System initiative.

---

**Last Updated**: December 9, 2025  
**Status**: ✅ Production Ready  
**Current Version**: 1.0.0  
**Maintained By**: CyberGuard Team
