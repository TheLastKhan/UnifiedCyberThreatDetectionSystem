# API Usage Examples

Unified Cyber Threat Detection System API'sini kullanmak için örnekler.

## Temel URL

```
Development: http://localhost:5000/api/v1
Production: https://api.unifiedthreat.com/v1
```

## 1. Health Check

Sistem sağlığını kontrol etme.

### Request

```bash
curl -X GET http://localhost:5000/api/v1/health
```

### Python Örneği

```python
import requests

response = requests.get('http://localhost:5000/api/v1/health')
print(response.json())
```

### Response

```json
{
  "status": "healthy",
  "timestamp": "2024-12-07T10:30:00Z",
  "version": "1.0.0",
  "components": {
    "email_detector": "ready",
    "web_analyzer": "ready",
    "unified_platform": "ready"
  }
}
```

---

## 2. Email Phishing Detection

### Request

```bash
curl -X POST http://localhost:5000/api/v1/email/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "email_text": "Click here to verify your account: http://fake-bank.com",
    "sender": "noreply@phishing-site.com",
    "subject": "Urgent: Verify Your Account"
  }'
```

### Python Örneği

```python
import requests

email_data = {
    "email_text": "Click here to verify your account: http://fake-bank.com",
    "sender": "noreply@phishing-site.com",
    "subject": "Urgent: Verify Your Account"
}

response = requests.post(
    'http://localhost:5000/api/v1/email/analyze',
    json=email_data
)

result = response.json()
print(f"Prediction: {'Phishing' if result['prediction'] == 1 else 'Legitimate'}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Risk Score: {result['risk_score']:.0f}/100")
print(f"Risk Level: {result['risk_level']}")

print("\nRisk Factors:")
for factor in result['risk_factors']:
    print(f"  - {factor['factor']}: {factor['importance']:.2f}")
    print(f"    Evidence: {factor['evidence']}")
```

### Response

```json
{
  "prediction": 1,
  "confidence": 0.92,
  "risk_score": 87,
  "risk_level": "critical",
  "risk_factors": [
    {
      "factor": "suspicious_links",
      "importance": 0.85,
      "evidence": "URLs pointing to non-legitimate domain"
    },
    {
      "factor": "urgency_language",
      "importance": 0.78,
      "evidence": "Urgent action required detected"
    }
  ],
  "analysis_time": 0.234,
  "timestamp": "2024-12-07T10:30:00Z"
}
```

---

## 3. Web Log Analysis

### Request

```bash
curl -X POST http://localhost:5000/api/v1/web/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "logs": [
      "192.168.1.100 - - [07/Dec/2024:10:30:00 +0000] \"GET /admin HTTP/1.1\" 200 1234",
      "192.168.1.101 - - [07/Dec/2024:10:30:01 +0000] \"POST /login HTTP/1.1\" 200 567",
      "192.168.1.102 - - [07/Dec/2024:10:30:02 +0000] \"GET /../../../../etc/passwd HTTP/1.1\" 401 0"
    ]
  }'
```

### Python Örneği

```python
import requests

log_data = {
    "logs": [
        "192.168.1.100 - - [07/Dec/2024:10:30:00 +0000] \"GET /admin HTTP/1.1\" 200 1234",
        "192.168.1.101 - - [07/Dec/2024:10:30:01 +0000] \"POST /login HTTP/1.1\" 200 567",
        "192.168.1.102 - - [07/Dec/2024:10:30:02 +0000] \"GET /../../../../etc/passwd HTTP/1.1\" 401 0"
    ]
}

response = requests.post(
    'http://localhost:5000/api/v1/web/analyze',
    json=log_data
)

result = response.json()
print(f"Anomalies Detected: {result['anomalies_detected']}")
print(f"Total Logs: {result['summary']['total_logs_analyzed']}")
print(f"Unique IPs: {result['summary']['unique_ips']}")

if result['summary']['high_risk_ips']:
    print(f"\nHigh Risk IPs: {result['summary']['high_risk_ips']}")

if result['summary']['suspected_attack_patterns']:
    print(f"\nSuspected Attacks:")
    for pattern in result['summary']['suspected_attack_patterns']:
        print(f"  - {pattern}")
```

### Response

```json
{
  "anomalies_detected": 1,
  "anomaly_scores": [
    {
      "log_index": 0,
      "ip_address": "192.168.1.100",
      "anomaly_score": 0.15,
      "is_anomaly": false,
      "risk_level": "normal",
      "indicators": ["normal_traffic"]
    },
    {
      "log_index": 2,
      "ip_address": "192.168.1.102",
      "anomaly_score": 0.89,
      "is_anomaly": true,
      "risk_level": "malicious",
      "indicators": ["path_traversal_attempt", "unauthorized_access"]
    }
  ],
  "summary": {
    "total_logs_analyzed": 3,
    "unique_ips": 3,
    "high_risk_ips": ["192.168.1.102"],
    "suspected_attack_patterns": ["directory_traversal"]
  },
  "analysis_time": 0.567,
  "timestamp": "2024-12-07T10:30:00Z"
}
```

---

## 4. Unified Threat Analysis

Email ve web verilerini birlikte analiz etme.

### Request

```bash
curl -X POST http://localhost:5000/api/v1/unified/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "email": {
      "text": "Click here to claim your prize: http://attacker-site.com/malware.exe",
      "sender": "attacker@fake-site.com",
      "subject": "You have won!"
    },
    "web_logs": [
      "192.168.1.100 - - [07/Dec/2024:10:30:00 +0000] \"GET /malware.exe HTTP/1.1\" 200 5000"
    ]
  }'
```

### Python Örneği

```python
import requests

threat_data = {
    "email": {
        "text": "Click here to claim your prize: http://attacker-site.com/malware.exe",
        "sender": "attacker@fake-site.com",
        "subject": "You have won!"
    },
    "web_logs": [
        "192.168.1.100 - - [07/Dec/2024:10:30:00 +0000] \"GET /malware.exe HTTP/1.1\" 200 5000"
    ]
}

response = requests.post(
    'http://localhost:5000/api/v1/unified/analyze',
    json=threat_data
)

result = response.json()
print(f"Threat ID: {result['threat_id']}")
print(f"Overall Risk Score: {result['overall_risk_score']:.0f}/100")
print(f"Overall Risk Level: {result['overall_risk_level']}")
print(f"Email Risk Score: {result['email_analysis']['risk_score']:.0f}")
print(f"Web Risk Score: {result['web_analysis']['summary']['high_risk_ips']}")
print(f"Correlation Score: {result['correlation_score']:.2f}")

print("\nCorrelated Threats:")
for threat in result['correlated_threats']:
    print(f"  - Email: {threat['email_risk_factor']}")
    print(f"    Web: {threat['web_indicator']}")
    print(f"    Strength: {threat['correlation_strength']:.2f}")

print("\nRecommendations:")
for rec in result['recommendations']:
    print(f"  - {rec}")
```

### Response

```json
{
  "threat_id": "THREAT-20241207-001",
  "overall_risk_score": 95,
  "overall_risk_level": "critical",
  "email_analysis": {
    "prediction": 1,
    "confidence": 0.95,
    "risk_score": 92,
    "risk_level": "critical",
    "risk_factors": [
      {
        "factor": "suspicious_links",
        "importance": 0.89,
        "evidence": "Link to attacker domain"
      },
      {
        "factor": "malware_distribution",
        "importance": 0.87,
        "evidence": "EXE file download attempt"
      }
    ]
  },
  "web_analysis": {
    "anomalies_detected": 1,
    "summary": {
      "total_logs_analyzed": 1,
      "high_risk_ips": ["192.168.1.100"],
      "suspected_attack_patterns": ["malware_distribution"]
    }
  },
  "correlation_score": 0.94,
  "correlated_threats": [
    {
      "email_risk_factor": "suspicious_links",
      "web_indicator": "malware_distribution",
      "correlation_strength": 0.94
    }
  ],
  "recommendations": [
    "Block attacker domain immediately",
    "Quarantine email and remove from user inboxes",
    "Monitor IP 192.168.1.100 for additional malicious activity",
    "Alert security team about coordinated attack"
  ],
  "timestamp": "2024-12-07T10:30:00Z"
}
```

---

## 5. Get Latest Reports

### Request

```bash
curl -X GET "http://localhost:5000/api/v1/reports/latest?limit=5"
```

### Python Örneği

```python
import requests

response = requests.get(
    'http://localhost:5000/api/v1/reports/latest',
    params={'limit': 5}
)

reports = response.json()
print(f"Total Reports: {reports['total']}")

for report in reports['reports']:
    print(f"\nReport ID: {report['report_id']}")
    print(f"Type: {report['analysis_type']}")
    print(f"Critical Threats: {report['threat_summary']['critical_count']}")
    print(f"High Threats: {report['threat_summary']['high_count']}")
    print(f"Generated: {report['generated_at']}")
```

---

## 6. Export Report

### Request

```bash
# JSON olarak
curl -X GET "http://localhost:5000/api/v1/reports/export/REPORT-001?format=json" \
  -o report.json

# PDF olarak
curl -X GET "http://localhost:5000/api/v1/reports/export/REPORT-001?format=pdf" \
  -o report.pdf

# CSV olarak
curl -X GET "http://localhost:5000/api/v1/reports/export/REPORT-001?format=csv" \
  -o report.csv
```

### Python Örneği

```python
import requests

# PDF indirme
response = requests.get(
    'http://localhost:5000/api/v1/reports/export/REPORT-001?format=pdf'
)

with open('threat_report.pdf', 'wb') as f:
    f.write(response.content)

print("Report downloaded as PDF")
```

---

## Error Handling

### Invalid Request

```json
{
  "error": "ValidationError",
  "message": "Invalid email text: minimum 10 characters required",
  "timestamp": "2024-12-07T10:30:00Z"
}
```

### Rate Limit

```json
{
  "error": "RateLimitError",
  "message": "Rate limit exceeded: 100 requests per minute",
  "details": {
    "limit": 100,
    "reset_in": 45
  }
}
```

### Server Error

```json
{
  "error": "InternalServerError",
  "message": "An unexpected error occurred",
  "details": {
    "request_id": "REQ-12345"
  }
}
```

---

## Best Practices

1. **Always include error handling**
   ```python
   try:
       response = requests.post(url, json=data)
       response.raise_for_status()
   except requests.exceptions.RequestException as e:
       print(f"API Error: {e}")
   ```

2. **Implement retry logic**
   ```python
   from tenacity import retry, stop_after_attempt, wait_exponential
   
   @retry(stop=stop_after_attempt(3), wait=wait_exponential())
   def call_api(url, data):
       return requests.post(url, json=data)
   ```

3. **Use connection pooling for multiple requests**
   ```python
   from requests.adapters import HTTPAdapter
   from requests.packages.urllib3.util.retry import Retry
   
   session = requests.Session()
   retry = Retry(connect=3, backoff_factor=0.5)
   adapter = HTTPAdapter(max_retries=retry)
   session.mount('http://', adapter)
   ```

4. **Validate input before sending**
   ```python
   from pydantic import BaseModel, validator
   
   class EmailAnalysisRequest(BaseModel):
       email_text: str
       sender: str = None
       subject: str = None
       
       @validator('email_text')
       def email_text_not_empty(cls, v):
           if len(v) < 10:
               raise ValueError('Email text must be at least 10 characters')
           return v
   ```

---

## SDK Örnekleri (Gelecekte)

Resmi SDK'lar yazılacaktır:
- Python SDK
- JavaScript/Node.js SDK
- Java SDK
- Go SDK

---

## Support

Sorularınız veya sorunlarınız varsa:
- Email: dev@unifiedthreat.local
- GitHub Issues: [Project Issues](https://github.com/TheLastKhan/UnifiedCyberThreatDetectionSystem/issues)
- Documentation: [Full API Docs](api.html)
