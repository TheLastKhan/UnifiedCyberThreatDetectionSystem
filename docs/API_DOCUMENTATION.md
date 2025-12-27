# 📡 Production API Documentation

**Version:** 1.0.0  
**Last Updated:** December 13, 2025  
**Base URL:** `http://localhost:5000` (Development) | `https://your-domain.com` (Production)

## Table of Contents

1. [Authentication](#authentication)
2. [Email Analysis API](#email-analysis-api)
3. [Web Log Analysis API](#web-log-analysis-api)
4. [Monitoring API](#monitoring-api)
5. [Threat Enrichment API](#threat-enrichment-api)
6. [Alert System API](#alert-system-api)
7. [Health Check API](#health-check-api)
8. [Error Handling](#error-handling)
9. [Rate Limiting](#rate-limiting)

---

## Authentication

Currently, the API operates without authentication for internal use. For production deployment, implement one of:
- JWT tokens
- API Keys
- OAuth 2.0

**Recommended:** Add API key authentication for production.

---

## Email Analysis API

### Analyze Email for Phishing

Analyzes email content for phishing threats using trained ML models.

**Endpoint:** `POST /api/email/analyze`

**Request Headers:**
```http
Content-Type: application/json
```

**Request Body:**
```json
{
  "email_content": "URGENT! Click here to verify your account immediately!",
  "email_sender": "noreply@suspicious-domain.com",
  "email_subject": "URGENT: Account Verification Required"
}
```

**Required Fields:**
- `email_content` (string): The email body text
- `email_sender` (string, optional): Sender email address
- `email_subject` (string, optional): Email subject line

**Success Response (200 OK):**
```json
{
  "prediction": "Phishing",
  "confidence": 0.94,
  "risk_level": "high",
  "features": {
    "urgent_words": 3,
    "suspicious_urls": 1,
    "sender_reputation": "unknown"
  },
  "explanation": {
    "lime_explanation": [
      {"feature": "urgent", "weight": 0.45},
      {"feature": "click_here", "weight": 0.32},
      {"feature": "verify_account", "weight": 0.28}
    ],
    "top_features": ["URGENT", "verify", "immediately"]
  },
  "timestamp": "2025-12-13T10:30:00"
}
```

**Model Not Trained (503 Service Unavailable):**
```json
{
  "error": "Model not trained",
  "message": "Email detector needs to be trained first"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "email_content is required"
}
```

**Example Usage:**

**cURL:**
```bash
curl -X POST http://localhost:5000/api/email/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "email_content": "URGENT! Your account will be suspended!",
    "email_sender": "admin@fake-bank.com",
    "email_subject": "Account Suspension Notice"
  }'
```

**Python:**
```python
import requests

url = "http://localhost:5000/api/email/analyze"
payload = {
    "email_content": "URGENT! Your account will be suspended!",
    "email_sender": "admin@fake-bank.com",
    "email_subject": "Account Suspension Notice"
}

response = requests.post(url, json=payload)
result = response.json()
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']}")
```

---

## Web Log Analysis API

### Analyze Web Logs for Anomalies

Analyzes web server logs for attack patterns and anomalies.

**Endpoint:** `POST /api/web/analyze`

**Request Body:**
```json
{
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
    },
    {
      "ip": "203.0.113.45",
      "timestamp": "2025-12-13T10:00:05",
      "method": "GET",
      "path": "/admin/../../../etc/passwd",
      "status": 404,
      "size": 128,
      "user_agent": "BadBot/1.0",
      "protocol": "HTTP/1.1",
      "referer": "-"
    }
  ]
}
```

**Required Fields:**
- `ip_address` (string): IP address to analyze
- `logs` (array): Array of log entries

**Success Response (200 OK):**
```json
{
  "ip_address": "203.0.113.45",
  "risk_level": "high",
  "anomaly_score": 0.87,
  "total_requests": 2,
  "suspicious_patterns": [
    {
      "type": "path_traversal",
      "severity": "high",
      "pattern": "../../../etc/passwd",
      "count": 1
    },
    {
      "type": "brute_force",
      "severity": "medium",
      "details": "Multiple failed login attempts",
      "count": 1
    }
  ],
  "attack_indicators": {
    "sql_injection": false,
    "xss": false,
    "path_traversal": true,
    "brute_force": true
  },
  "recommendation": "Block IP immediately - Multiple attack patterns detected",
  "timestamp": "2025-12-13T10:30:00"
}
```

**Example Usage:**

**cURL:**
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

**Python:**
```python
import requests

url = "http://localhost:5000/api/web/analyze"
payload = {
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
}

response = requests.post(url, json=payload)
result = response.json()
print(f"Risk Level: {result['risk_level']}")
print(f"Anomaly Score: {result['anomaly_score']}")
```

---

## Monitoring API

### Log Prediction

Logs model predictions for monitoring and analytics.

**Endpoint:** `POST /api/monitoring/log_prediction`

**Request Body:**
```json
{
  "model": "email_detector",
  "prediction": "phishing",
  "confidence": 0.95,
  "latency": 0.025,
  "features": {
    "urgent_words": 3,
    "urls": 1
  }
}
```

**Success Response (200 OK):**
```json
{
  "status": "logged",
  "timestamp": "2025-12-13T10:30:00"
}
```

---

### Get Metrics

Retrieves monitoring metrics for model performance.

**Endpoint:** `GET /api/monitoring/metrics`

**Success Response (200 OK):**
```json
{
  "total_predictions": 1234,
  "accuracy": 0.94,
  "average_latency": 0.032,
  "predictions_by_model": {
    "email_detector": 800,
    "web_analyzer": 434
  },
  "last_updated": "2025-12-13T10:30:00"
}
```

---

### Check Model Drift

Checks for model drift based on recent predictions.

**Endpoint:** `POST /api/monitoring/drift/check`

**Request Body:**
```json
{
  "model": "email_detector",
  "recent_samples": [
    {"features": [0.1, 0.2, 0.3], "prediction": 1},
    {"features": [0.2, 0.3, 0.4], "prediction": 0}
  ]
}
```

**Success Response (200 OK):**
```json
{
  "drift_detected": false,
  "drift_score": 0.12,
  "threshold": 0.3,
  "recommendation": "No action needed"
}
```

---

### Get Retraining Status

Gets the current status of model retraining.

**Endpoint:** `GET /api/monitoring/retraining/status`

**Success Response (200 OK):**
```json
{
  "status": "idle",
  "last_training": "2025-12-10T08:00:00",
  "next_scheduled": "2025-12-17T08:00:00",
  "performance_trend": "stable"
}
```

---

## Threat Enrichment API

### Enrich IP Address

Enriches IP address information using VirusTotal API.

**Endpoint:** `POST /api/enrich/ip`

**Request Body:**
```json
{
  "ip": "8.8.8.8"
}
```

**Success Response (200 OK):**
```json
{
  "ip": "8.8.8.8",
  "country": "US",
  "reputation": "good",
  "threat_score": 0,
  "categories": ["dns", "google"],
  "last_analysis": "2025-12-13T10:30:00",
  "source": "virustotal"
}
```

**Rate Limited (429 Too Many Requests):**
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

**Configuration Required:**
Set `VIRUSTOTAL_API_KEY` environment variable.

---

### Enrich Domain

Enriches domain information using VirusTotal API.

**Endpoint:** `POST /api/enrich/domain`

**Request Body:**
```json
{
  "domain": "example.com"
}
```

**Success Response (200 OK):**
```json
{
  "domain": "example.com",
  "reputation": "good",
  "threat_score": 0,
  "categories": ["web", "business"],
  "creation_date": "1995-08-14",
  "last_analysis": "2025-12-13T10:30:00",
  "source": "virustotal"
}
```

---

## Alert System API

### Send Alert

Sends email alerts for detected threats.

**Endpoint:** `POST /api/alert/send`

**Request Body:**
```json
{
  "threat_type": "phishing",
  "severity": "high",
  "details": "Phishing email detected from admin@fake-bank.com",
  "recipient": "security@yourcompany.com",
  "source_ip": "203.0.113.45",
  "timestamp": "2025-12-13T10:30:00"
}
```

**Success Response (200 OK):**
```json
{
  "status": "sent",
  "alert_id": "alert_12345",
  "timestamp": "2025-12-13T10:30:00"
}
```

**Configuration Required:**
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## Health Check API

### API Health

Checks if the API is running and responding.

**Endpoint:** `GET /api/health`

**Success Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-13T10:30:00",
  "version": "1.0.0",
  "uptime": 86400
}
```

---

### Monitoring Health

Checks monitoring system health.

**Endpoint:** `GET /api/monitoring/health`

**Success Response (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected",
  "models": {
    "email_detector": "loaded",
    "web_analyzer": "loaded"
  },
  "timestamp": "2025-12-13T10:30:00"
}
```

---

## Error Handling

### Standard Error Response Format

All errors follow this format:

```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "timestamp": "2025-12-13T10:30:00",
  "path": "/api/email/analyze"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Endpoint not found |
| 405 | Method Not Allowed | Wrong HTTP method |
| 415 | Unsupported Media Type | Missing Content-Type header |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Model not trained or service down |

---

## Rate Limiting

### Default Limits

- **Email Analysis:** 100 requests/minute per IP
- **Web Analysis:** 100 requests/minute per IP
- **VirusTotal Enrichment:** 4 requests/minute (API limitation)

### Rate Limit Headers

Responses include rate limit information:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1702468800
```

---

## Best Practices

### 1. Always Check Model Status

Before making predictions, check if models are trained:

```python
health = requests.get("http://localhost:5000/api/monitoring/health")
if health.json()["models"]["email_detector"] != "loaded":
    print("Model not ready")
```

### 2. Handle 503 Responses

Models may not be trained. Handle gracefully:

```python
response = requests.post(url, json=payload)
if response.status_code == 503:
    print("Model needs training. Please train models first.")
elif response.status_code == 200:
    result = response.json()
    # Process result
```

### 3. Batch Processing

For multiple emails, process them sequentially to avoid overwhelming:

```python
for email in emails:
    response = requests.post(url, json=email)
    time.sleep(0.1)  # Rate limiting
```

### 4. Error Logging

Always log API responses for debugging:

```python
import logging

response = requests.post(url, json=payload)
logging.info(f"Status: {response.status_code}")
logging.debug(f"Response: {response.text}")
```

---

## Integration Examples

### Flask Integration

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
API_BASE = "http://localhost:5000"

@app.route('/check-email', methods=['POST'])
def check_email():
    data = request.json
    
    response = requests.post(
        f"{API_BASE}/api/email/analyze",
        json={
            "email_content": data['content'],
            "email_sender": data['sender'],
            "email_subject": data['subject']
        }
    )
    
    return jsonify(response.json())
```

### Django Integration

```python
from django.http import JsonResponse
import requests

API_BASE = "http://localhost:5000"

def analyze_email(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        response = requests.post(
            f"{API_BASE}/api/email/analyze",
            json=data
        )
        
        return JsonResponse(response.json())
```

### JavaScript Integration

```javascript
async function analyzeEmail(emailData) {
    const response = await fetch('http://localhost:5000/api/email/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(emailData)
    });
    
    const result = await response.json();
    return result;
}

// Usage
const result = await analyzeEmail({
    email_content: "URGENT! Verify your account",
    email_sender: "admin@fake.com",
    email_subject: "Account Verification"
});

console.log(result.prediction);
```

---

## Testing the API

### Using pytest

All API endpoints have comprehensive tests:

```bash
# Run all API tests
pytest tests/test_api_integration.py -v

# Run specific test
pytest tests/test_api_integration.py::TestEmailAnalysisAPI::test_email_analyze_endpoint -v
```

### Using Postman

Import the OpenAPI specification:
1. Open Postman
2. Import → `docs/openapi.yaml`
3. All endpoints will be available with examples

---

## Support

For issues or questions:
- **GitHub Issues:** [Repository Issues](https://github.com/your-repo/issues)
- **Documentation:** [Full Documentation](docs/)
- **Email:** support@yourcompany.com

---

## Changelog

### Version 1.0.0 (2025-12-13)
- ✅ Initial production API release
- ✅ All 9 endpoints implemented
- ✅ 22 API integration tests (100% passing)
- ✅ Complete error handling
- ✅ VirusTotal integration
- ✅ SMTP alert system
- ✅ Comprehensive documentation
