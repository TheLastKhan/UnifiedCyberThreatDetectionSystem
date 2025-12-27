# 📚 User Guide - Unified Cyber Threat Detection System

**Complete guide for installing, configuring, and using the system.**

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Training Models](#training-models)
5. [Using the Dashboard](#using-the-dashboard)
6. [API Usage](#api-usage)
7. [Database Management](#database-management)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

Get up and running in 5 minutes:

```bash
# 1. Clone repository
git clone https://github.com/TheLastKhan/UnifiedCyberThreatDetectionSystem
cd UnifiedCyberThreatDetectionSystem

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure production settings
python configure_production.py

# 5. Train models (first time only)
python main.py

# 6. Start dashboard
python run_dashboard.py
```

Open browser: http://localhost:5000

---

## Installation

### System Requirements

- **Operating System:** Windows 10+, Ubuntu 20.04+, macOS 10.15+
- **Python:** 3.8 or higher
- **RAM:** 4GB minimum, 8GB recommended
- **Disk Space:** 2GB free space
- **Internet:** Required for package installation and VirusTotal API

### Step 1: Install Python

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run installer, **check "Add Python to PATH"**
3. Verify: `python --version`

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**macOS:**
```bash
brew install python@3.10
```

### Step 2: Clone Repository

```bash
git clone https://github.com/TheLastKhan/UnifiedCyberThreatDetectionSystem
cd UnifiedCyberThreatDetectionSystem
```

### Step 3: Create Virtual Environment

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- Flask (Web framework)
- Scikit-learn (ML models)
- Pandas, NumPy (Data processing)
- SQLAlchemy (Database)
- LIME, SHAP (Explainability)
- And more...

**Installation Time:** 2-5 minutes depending on internet speed.

### Step 5: Verify Installation

```bash
python test_installation.py
```

Expected output:
```
✓ Python version: 3.10.10
✓ All required packages installed
✓ Database connection successful
✓ Models directory exists
✓ Data directory exists
✓ Installation successful!
```

---

## Configuration

### Interactive Configuration (Recommended)

Run the configuration wizard:

```bash
python configure_production.py
```

The wizard will guide you through:
1. ✅ Database configuration
2. ✅ VirusTotal API key
3. ✅ SMTP email settings
4. ✅ Security settings
5. ✅ Logging configuration

**Configuration is saved to:** `.env.production`

### Manual Configuration

Create `.env.production` file:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./threat_detection.db
# Or PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/threat_detection

# VirusTotal API (for threat enrichment)
VIRUSTOTAL_API_KEY=your_virustotal_api_key_here
VT_API_KEY=your_virustotal_api_key_here

# SMTP Configuration (for alerts)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Security
SECRET_KEY=your-secret-key-here-change-this
FLASK_ENV=production

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/application.log
```

### Getting API Keys

**VirusTotal API Key:**
1. Go to [VirusTotal](https://www.virustotal.com/)
2. Sign up for free account
3. Go to Profile → API Key
4. Copy your API key
5. Free tier: 4 requests/minute

**Gmail SMTP (for alerts):**
1. Enable 2-Factor Authentication
2. Go to Google Account → Security
3. Generate App Password
4. Use app password in SMTP_PASSWORD

---

## Training Models

### First Time Training

Models need to be trained before use:

```bash
python main.py
```

**Training Process:**
```
📧 Training Email Phishing Detector...
   ├─ Loading datasets (4500+ emails)
   ├─ Feature extraction
   ├─ Training Stacking Ensemble
   ├─ Training Voting Ensemble
   └─ Saved to models/
   ✅ Complete! (30-60 seconds)

🌐 Training Web Log Analyzer...
   ├─ Loading log data
   ├─ Training Isolation Forest
   ├─ Training pattern detectors
   └─ Saved to models/
   ✅ Complete! (10-20 seconds)

✅ All models trained successfully!
```

**Model Files Created:**
- `models/email_detector_stacking.pkl` (35MB)
- `models/email_detector_voting.pkl` (32MB)
- `models/tfidf_vectorizer.pkl` (15MB)
- `models/web_anomaly_detector.pkl` (8MB)

### Retraining Models

Retrain with new data:

```bash
# Add your data to dataset/ folder
# Then retrain
python main.py --retrain
```

**When to Retrain:**
- New phishing patterns emerge
- Model accuracy drops below 90%
- Monthly maintenance
- After adding new training data

---

## Using the Dashboard

### Starting the Dashboard

```bash
python run_dashboard.py
```

Output:
```
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.100:5000
```

Open browser: http://localhost:5000

### Dashboard Features

#### 1. Email Analysis Tab

**Analyze Single Email:**
1. Paste email content
2. Enter sender email
3. Enter subject
4. Click "Analyze Email"

**Results Show:**
- ✅ Prediction: Safe / Phishing
- 📊 Confidence Score
- 🎯 Risk Level
- 📝 LIME Explanation
- 🔍 Feature Analysis

#### 2. Web Log Analysis Tab

**Analyze Web Logs:**
1. Paste Apache/Nginx logs
2. Enter IP to analyze
3. Click "Analyze Logs"

**Results Show:**
- 🚨 Risk Level
- 📊 Anomaly Score
- ⚠️ Attack Patterns Detected
- 💡 Recommendations

#### 3. Unified Analysis Tab

**Cross-Platform Correlation:**
1. Upload both email and web logs
2. System correlates threats
3. Shows combined risk assessment

#### 4. Model Comparison Tab

**Compare Model Performance:**
- Stacking vs Voting Ensemble
- Accuracy metrics
- Confusion matrices
- Feature importance

#### 5. Statistics Dashboard

**System Statistics:**
- Total emails analyzed
- Total web logs processed
- Threats detected
- Average confidence
- Charts and graphs

---

## API Usage

### Starting the API Server

```bash
python run_dashboard.py
```

API runs on: http://localhost:5000/api

### Quick API Examples

#### Analyze Email (Python)

```python
import requests

url = "http://localhost:5000/api/email/analyze"
data = {
    "email_content": "URGENT! Verify your account now!",
    "email_sender": "admin@fake-bank.com",
    "email_subject": "Account Verification"
}

response = requests.post(url, json=data)
result = response.json()

print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']}")
```

#### Analyze Web Logs (cURL)

```bash
curl -X POST http://localhost:5000/api/web/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "203.0.113.45",
    "logs": [
      {
        "ip": "203.0.113.45",
        "timestamp": "2025-12-13T10:00:00",
        "method": "POST",
        "path": "/admin/login",
        "status": 401,
        "size": 256,
        "user_agent": "BadBot/1.0",
        "protocol": "HTTP/1.1",
        "referer": "-"
      }
    ]
  }'
```

**Full API documentation:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

## Database Management

### Using SQLite (Default)

SQLite is used by default - no setup needed!

**Database file:** `threat_detection.db`

**View data:**
```bash
sqlite3 threat_detection.db
.tables
SELECT * FROM emails LIMIT 5;
.exit
```

### Using PostgreSQL (Production)

**1. Install PostgreSQL:**

Windows: Download from [postgresql.org](https://www.postgresql.org/download/)

Ubuntu:
```bash
sudo apt install postgresql postgresql-contrib
```

**2. Create Database:**
```bash
sudo -u postgres psql
CREATE DATABASE threat_detection;
CREATE USER threat_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE threat_detection TO threat_user;
\q
```

**3. Update Configuration:**
```bash
# In .env.production
DATABASE_URL=postgresql://threat_user:secure_password@localhost:5432/threat_detection
```

**4. Initialize Database:**
```bash
python -c "from src.database.connection import DatabaseConnection; DatabaseConnection().create_tables()"
```

### Database Operations

**Import CSV Data:**
```python
from src.utils.data_loader import DataLoader

loader = DataLoader()
loader.import_emails_to_database('dataset/phishing_email.csv')
```

**Query Database:**
```python
from src.database.connection import DatabaseConnection

db = DatabaseConnection()
session = db.get_session()

# Get all phishing emails
from src.database.models import Email
phishing_emails = session.query(Email).filter_by(is_phishing=True).all()

print(f"Found {len(phishing_emails)} phishing emails")
```

**Backup Database:**
```bash
# SQLite
cp threat_detection.db threat_detection_backup.db

# PostgreSQL
pg_dump threat_detection > backup.sql
```

---

## Troubleshooting

### Common Issues

#### 1. Models Not Trained

**Error:**
```
Model not trained. Please train models first.
```

**Solution:**
```bash
python main.py
```

#### 2. Port Already in Use

**Error:**
```
Address already in use
```

**Solution:**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9

# Or use different port
python run_dashboard.py --port 8080
```

#### 3. Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
```bash
# Ensure virtual environment is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

#### 4. Database Connection Failed

**Error:**
```
Could not connect to database
```

**Solution:**
```bash
# Check DATABASE_URL in .env.production
# For PostgreSQL, ensure service is running:
sudo systemctl status postgresql  # Linux
# Start if stopped:
sudo systemctl start postgresql
```

#### 5. VirusTotal API Rate Limit

**Error:**
```
Rate limit exceeded
```

**Solution:**
- Free tier: 4 requests/minute
- Wait 60 seconds between batches
- Or upgrade to paid plan

#### 6. SMTP Authentication Failed

**Error:**
```
SMTP authentication failed
```

**Solution:**
- Use Gmail App Password (not account password)
- Enable "Less secure app access" (if available)
- Check firewall allows port 587

### Getting Help

**1. Check Logs:**
```bash
tail -f logs/application.log
```

**2. Run Tests:**
```bash
pytest tests/ -v
```

**3. Verify Installation:**
```bash
python test_installation.py
```

**4. Check System Status:**
```bash
curl http://localhost:5000/api/health
```

---

## Best Practices

### Security

1. **Never commit `.env.production` to Git**
2. Use strong SECRET_KEY (32+ characters)
3. Change default passwords
4. Enable HTTPS in production
5. Regularly update dependencies

### Performance

1. **Use PostgreSQL for production** (not SQLite)
2. Enable database connection pooling
3. Cache frequently accessed data
4. Monitor memory usage
5. Retrain models monthly

### Maintenance

1. **Backup database weekly**
2. Review logs daily
3. Update models with new data
4. Test after updates
5. Monitor API rate limits

---

## Next Steps

After installation and configuration:

1. ✅ **Train models** - `python main.py`
2. ✅ **Start dashboard** - `python run_dashboard.py`
3. ✅ **Test with sample data** - Use demo files in `data/samples/`
4. ✅ **Read API docs** - [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
5. ✅ **Configure alerts** - Set up SMTP for threat notifications
6. ✅ **Import your data** - Add to `dataset/` and retrain

---

## Additional Resources

- **API Documentation:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Configuration Guide:** [PRODUCTION_CONFIG_GUIDE.md](PRODUCTION_CONFIG_GUIDE.md)
- **Testing Guide:** [TESTING_QA_DOCUMENTATION.md](TESTING_QA_DOCUMENTATION.md)
- **Deployment Guide:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Architecture:** [architecture.html](architecture.html)

---

## Support

Need help?

- **GitHub Issues:** [Report an issue](https://github.com/TheLastKhan/UnifiedCyberThreatDetectionSystem/issues)
- **Documentation:** Check `docs/` folder
- **Email:** support@yourcompany.com

---

**Version:** 1.0.0  
**Last Updated:** December 13, 2025  
**System Status:** ✅ Production Ready
