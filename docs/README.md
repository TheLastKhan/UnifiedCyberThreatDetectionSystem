# 📚 Documentation Index

**Complete documentation for Unified Cyber Threat Detection System**

---

## 🚀 Quick Start

New to the system? Start here:

1. **[USER_GUIDE.md](USER_GUIDE.md)** - Complete installation and usage guide
2. **[README.md](../README.md)** - Project overview and quick start
3. **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - REST API reference

---

## 📖 Documentation Structure

### 🎯 For Users

| Document | Description | Best For |
|----------|-------------|----------|
| **[USER_GUIDE.md](USER_GUIDE.md)** | Complete installation, configuration, and usage guide | New users, installation, daily use |
| **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** | REST API reference with examples | Developers integrating the API |
| **[TESTING_GUIDE.md](TESTING_GUIDE.md)** | How to run and write tests | QA engineers, contributors |
| **[USAGE_SCENARIOS.md](USAGE_SCENARIOS.md)** | Real-world usage examples | Understanding capabilities |

### 🏗️ For Developers

| Document | Description | Best For |
|----------|-------------|----------|
| **[architecture.html](architecture.html)** | System architecture diagrams | Understanding design |
| **[api.html](api.html)** | Interactive API documentation (Swagger) | API exploration |
| **[openapi.yaml](openapi.yaml)** | OpenAPI 3.1.0 specification | API integration |
| **[BEST_PRACTICES.md](BEST_PRACTICES.md)** | Development best practices | Code quality |

### 🔧 For Operations

| Document | Description | Best For |
|----------|-------------|----------|
| **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** | Production deployment guide | DevOps, deployment |
| **[PRODUCTION_CONFIG_GUIDE.md](PRODUCTION_CONFIG_GUIDE.md)** | Production configuration | System administrators |
| **[DATABASE_MIGRATION.md](DATABASE_MIGRATION.md)** | Database setup and migration | Database administrators |
| **[MONITORING_API.md](MONITORING_API.md)** | Monitoring and metrics | Operations teams |

### 📊 Project Status

| Document | Description | Best For |
|----------|-------------|----------|
| **[PROJECT_STATUS.md](PROJECT_STATUS.md)** | Current project status | Management, stakeholders |
| **[WHAT_IS_READY_NOW.md](WHAT_IS_READY_NOW.md)** | Production readiness checklist | Deployment planning |
| **[TESTING_QA_DOCUMENTATION.md](TESTING_QA_DOCUMENTATION.md)** | QA and testing documentation | Quality assurance |

---

## 🎓 Learning Path

### Beginner Path

1. Read [README.md](../README.md) for overview
2. Follow [USER_GUIDE.md](USER_GUIDE.md) for installation
3. Try [USAGE_SCENARIOS.md](USAGE_SCENARIOS.md) examples
4. Explore the dashboard at http://localhost:5000

### Developer Path

1. Read [architecture.html](architecture.html) for system design
2. Study [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
3. Review [BEST_PRACTICES.md](BEST_PRACTICES.md)
4. Run tests following [TESTING_GUIDE.md](TESTING_GUIDE.md)
5. Contribute code

### Operations Path

1. Review [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. Configure using [PRODUCTION_CONFIG_GUIDE.md](PRODUCTION_CONFIG_GUIDE.md)
3. Set up database via [DATABASE_MIGRATION.md](DATABASE_MIGRATION.md)
4. Monitor with [MONITORING_API.md](MONITORING_API.md)

---

## 📋 Quick Reference

### Installation

```bash
# Clone and install
git clone <repo>
cd UnifiedCyberThreatDetectionSystem
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Configure
python configure_production.py

# Train models
python main.py

# Start dashboard
python run_dashboard.py
```

**Details:** [USER_GUIDE.md](USER_GUIDE.md)

### API Endpoints

```bash
# Email Analysis
POST /api/email/analyze

# Web Log Analysis
POST /api/web/analyze

# Health Check
GET /api/health
```

**Details:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

### Running Tests

```bash
# All tests
pytest -v

# Specific category
pytest tests/test_api_integration.py -v

# Without slow tests
pytest -m "not slow" -v
```

**Details:** [TESTING_GUIDE.md](TESTING_GUIDE.md)

---

## 🎯 Features Documentation

### Email Phishing Detection

- **Models:** Stacking & Voting Ensembles
- **Features:** NLP, URL analysis, sender reputation
- **Accuracy:** 94%+
- **Explainability:** LIME & SHAP

**Docs:** [USER_GUIDE.md#email-analysis](USER_GUIDE.md#using-the-dashboard)

### Web Log Analysis

- **Models:** Isolation Forest, Pattern Matching
- **Detects:** SQL Injection, XSS, Path Traversal, Brute Force
- **Performance:** < 5s for 100 logs
- **Explainability:** Feature importance, attack patterns

**Docs:** [USER_GUIDE.md#web-log-analysis](USER_GUIDE.md#using-the-dashboard)

### Cross-Platform Correlation

- **Correlation Engine:** Combines email and web threats
- **Risk Amplification:** Identifies coordinated attacks
- **Unified Reports:** Single view of all threats

**Docs:** [USAGE_SCENARIOS.md](USAGE_SCENARIOS.md)

### Dashboard & API

- **Web Interface:** Flask-based interactive dashboard
- **REST API:** 9 production endpoints
- **Real-time:** Live threat analysis
- **Monitoring:** Performance metrics and drift detection

**Docs:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

## 📊 System Specifications

### Technical Stack

- **Language:** Python 3.10+
- **Framework:** Flask 3.0+
- **ML Libraries:** Scikit-learn, TensorFlow (optional)
- **Database:** SQLite (dev), PostgreSQL (prod)
- **Explainability:** LIME, SHAP
- **Testing:** pytest (105 tests, 100% passing)

### Performance Metrics

- **Email Analysis:** < 100ms per email
- **Web Log Analysis:** < 5s per 100 logs
- **API Response Time:** < 200ms average
- **Model Accuracy:** 94%+ for email, 90%+ for web
- **Uptime:** 99.9% target

### Security Features

- **Input Validation:** All user inputs sanitized
- **SQL Injection Protection:** Parameterized queries
- **XSS Protection:** Content Security Policy
- **Rate Limiting:** 100 req/min per IP
- **Audit Logging:** All actions logged

---

## 🔍 Finding Specific Information

### "How do I...?"

| Question | Answer In |
|----------|-----------|
| Install the system? | [USER_GUIDE.md](USER_GUIDE.md#installation) |
| Train models? | [USER_GUIDE.md](USER_GUIDE.md#training-models) |
| Use the API? | [API_DOCUMENTATION.md](API_DOCUMENTATION.md) |
| Deploy to production? | [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) |
| Run tests? | [TESTING_GUIDE.md](TESTING_GUIDE.md) |
| Configure VirusTotal? | [USER_GUIDE.md](USER_GUIDE.md#configuration) |
| Set up SMTP alerts? | [PRODUCTION_CONFIG_GUIDE.md](PRODUCTION_CONFIG_GUIDE.md) |
| Troubleshoot errors? | [USER_GUIDE.md](USER_GUIDE.md#troubleshooting) |

### "What is...?"

| Question | Answer In |
|----------|-----------|
| The system architecture? | [architecture.html](architecture.html) |
| The API specification? | [openapi.yaml](openapi.yaml) |
| Test coverage? | [TESTING_GUIDE.md](TESTING_GUIDE.md) |
| Production readiness? | [WHAT_IS_READY_NOW.md](WHAT_IS_READY_NOW.md) |
| Database schema? | [DATABASE_MIGRATION.md](DATABASE_MIGRATION.md) |
| Best practices? | [BEST_PRACTICES.md](BEST_PRACTICES.md) |

---

## 📝 Contributing

### Documentation

Help improve documentation:

1. **Report Issues:** Documentation bugs or unclear sections
2. **Suggest Improvements:** Better explanations or examples
3. **Add Examples:** Real-world use cases
4. **Translate:** Help translate to other languages

### Standards

- Use Markdown for all docs
- Include code examples
- Keep language clear and concise
- Update index when adding new docs
- Version all documents

---

## 🆕 Latest Updates

### December 13, 2025

✅ **New Documentation:**
- Complete API documentation with examples
- Comprehensive user guide
- Testing guide with 105 test coverage
- Updated README with test results

✅ **System Updates:**
- Production API fully implemented (9 endpoints)
- All 105 tests passing (100%)
- VirusTotal integration
- SMTP alert system
- Complete error handling

---

## 🔗 External Resources

### Related Projects

- **Flask:** [flask.palletsprojects.com](https://flask.palletsprojects.com/)
- **Scikit-learn:** [scikit-learn.org](https://scikit-learn.org/)
- **LIME:** [github.com/marcotcr/lime](https://github.com/marcotcr/lime)
- **VirusTotal API:** [virustotal.com/api](https://www.virustotal.com/api/)

### Learning Resources

- **Machine Learning:** [coursera.org/ml](https://www.coursera.org/)
- **Cybersecurity:** [cybrary.it](https://www.cybrary.it/)
- **Flask Development:** [realpython.com/flask](https://realpython.com/)
- **pytest:** [docs.pytest.org](https://docs.pytest.org/)

---

## 📧 Support

### Getting Help

- **GitHub Issues:** Report bugs or request features
- **Documentation:** Search this documentation
- **Stack Overflow:** Tag `unified-threat-detection`
- **Email:** support@yourcompany.com

### Community

- **Discord:** Join our community server
- **Twitter:** Follow @ThreatDetection
- **Blog:** blog.yourcompany.com

---

## 📜 License

This project is licensed under the MIT License.

See [LICENSE](../LICENSE) file for details.

---

**Documentation Version:** 1.0.0  
**Last Updated:** December 13, 2025  
**Maintained By:** Development Team  
**Status:** ✅ Complete & Up to Date
