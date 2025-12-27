# ML Model Monitoring API Documentation

## AŞAMA 9: ML Model Monitoring & Drift Detection

### Overview
Comprehensive ML model monitoring system with real-time metrics tracking, data drift detection, A/B testing, and automated retraining pipelines.

### Base URL
```
http://localhost:5000/api/monitoring
```

---

## Endpoints

### 1. Metrics Tracking

#### Get Model Metrics
```http
GET /metrics/{model_name}
```

**Response:**
```json
{
  "status": "success",
  "model": "email_detector",
  "metrics": {
    "current": {
      "timestamp": "2025-12-13T17:30:00Z",
      "accuracy": 0.9542,
      "precision": 0.9634,
      "recall": 0.9421,
      "f1_score": 0.9526,
      "avg_prediction_time": 0.0234
    },
    "history": [ ... ],
    "total_predictions": 15234
  }
}
```

#### Compare Models
```http
GET /metrics/compare
```

**Response:**
```json
{
  "status": "success",
  "comparison": {
    "models": {
      "email_detector": { ... },
      "web_analyzer": { ... }
    },
    "best_accuracy": {
      "model": "email_detector",
      "value": 0.9542
    },
    "best_f1": {
      "model": "email_detector",
      "value": 0.9526
    },
    "fastest": {
      "model": "web_analyzer",
      "value": 0.0156
    }
  }
}
```

#### Log Prediction
```http
POST /metrics/log
```

**Request Body:**
```json
{
  "model_name": "email_detector",
  "input_data": {
    "subject": "Urgent: Account Verification",
    "sender": "noreply@suspicious.com"
  },
  "prediction": "phishing",
  "confidence": 0.95,
  "prediction_time": 0.123,
  "ground_truth": "phishing"
}
```

---

### 2. Drift Detection

#### Check for Drift
```http
POST /drift/{model_name}/check
```

**Response:**
```json
{
  "status": "success",
  "drift_report": {
    "timestamp": "2025-12-13T17:30:00Z",
    "model": "email_detector",
    "drift_detected": true,
    "severity": "medium",
    "features": {
      "subject_length": {
        "psi": 0.2134,
        "kl_divergence": 0.0876,
        "ks_statistic": 0.1234,
        "ks_pvalue": 0.0234,
        "drift_detected": true,
        "methods": {
          "psi": "drift",
          "ks_test": "drift"
        }
      }
    },
    "drift_count": 3,
    "total_features": 10,
    "max_psi": 0.2134
  }
}
```

#### Get Drift Summary
```http
GET /drift/{model_name}/summary
```

**Response:**
```json
{
  "status": "success",
  "model": "email_detector",
  "drift_summary": {
    "total_checks": 45,
    "drift_detected_count": 8,
    "drift_ratio": 0.1778,
    "latest_check": { ... },
    "history": [ ... ]
  }
}
```

#### Add Drift Sample
```http
POST /drift/{model_name}/sample
```

**Request Body:**
```json
{
  "features": {
    "subject_length": 45,
    "url_count": 2,
    "suspicious_words": 5
  }
}
```

---

### 3. A/B Testing

#### Get A/B Test Status
```http
GET /abtest/{experiment_name}/status
```

**Response:**
```json
{
  "status": "success",
  "summary": {
    "experiment": "email_model_comparison",
    "start_time": "2025-12-10T10:00:00Z",
    "duration_seconds": 259200,
    "total_requests": 15000,
    "variants": ["model_v1", "model_v2"],
    "traffic_allocation": {
      "model_v1": 50.0,
      "model_v2": 50.0
    },
    "statistics": { ... }
  }
}
```

#### Compare A/B Test Variants
```http
GET /abtest/{experiment_name}/compare
```

**Response:**
```json
{
  "status": "success",
  "comparison": {
    "experiment": "email_model_comparison",
    "timestamp": "2025-12-13T17:30:00Z",
    "total_requests": 15000,
    "best_accuracy": {
      "variant": "model_v2",
      "value": 0.9612
    },
    "best_speed": {
      "variant": "model_v1",
      "value": 0.0198
    },
    "variants": {
      "model_v1": {
        "accuracy": 0.9542,
        "avg_prediction_time": 0.0198,
        "traffic_allocation": 50.0,
        "actual_traffic": 49.8
      },
      "model_v2": {
        "accuracy": 0.9612,
        "avg_prediction_time": 0.0234,
        "traffic_allocation": 50.0,
        "actual_traffic": 50.2
      }
    },
    "recommendation": {
      "action": "promote",
      "winner": "model_v2",
      "reason": "model_v2 shows 0.7% improvement over model_v1",
      "confidence": "medium"
    }
  }
}
```

---

### 4. Auto-Retraining

#### Get Retraining Status
```http
GET /retraining/{model_name}/status
```

**Response:**
```json
{
  "status": "success",
  "model": "email_detector",
  "retraining_summary": {
    "total_retrainings": 5,
    "current_version": 6,
    "last_retraining": {
      "timestamp": "2025-12-10T08:00:00Z",
      "training_samples": 1500,
      "training_duration": 125.3,
      "validation_metrics": {
        "accuracy": 0.9634,
        "f1_score": 0.9587
      }
    },
    "buffer_size": 345
  },
  "buffer_stats": {
    "size": 345,
    "ready_for_training": true,
    "min_samples_needed": 100,
    "label_distribution": {
      "phishing": 178,
      "legitimate": 167
    }
  }
}
```

#### Check if Retraining Needed
```http
POST /retraining/{model_name}/check
```

**Request Body:**
```json
{
  "current_accuracy": 0.85,
  "drift_score": 0.15
}
```

**Response:**
```json
{
  "status": "success",
  "decision": {
    "should_retrain": false,
    "reasons": [
      "Accuracy 0.850 below threshold 0.800"
    ],
    "buffer_size": 345,
    "current_accuracy": 0.85,
    "drift_score": 0.15
  }
}
```

#### Add Training Sample
```http
POST /retraining/{model_name}/sample
```

**Request Body:**
```json
{
  "features": {
    "subject": "Win a free iPhone!",
    "sender": "prizes@scam.com",
    "url_count": 5
  },
  "label": "phishing",
  "metadata": {
    "source": "manual_review",
    "reviewer": "analyst_1"
  }
}
```

---

### 5. Health Check

#### Monitoring Health
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-13T17:30:00Z",
  "components": {
    "metrics_tracker": {
      "status": "operational",
      "tracked_models": 2
    },
    "drift_detectors": {
      "status": "operational",
      "active_detectors": 2
    },
    "ab_tests": {
      "status": "operational",
      "active_experiments": 1
    },
    "retraining_pipelines": {
      "status": "operational",
      "active_pipelines": 2
    }
  }
}
```

---

## Features

### 1. Model Performance Tracking
- Real-time accuracy, precision, recall, F1 score
- Prediction latency (avg, p95, p99)
- Confusion matrix tracking
- Historical metrics with trends

### 2. Data Drift Detection
- **PSI (Population Stability Index)**: < 0.1 stable, >= 0.2 drift
- **KL Divergence**: Distribution difference
- **Kolmogorov-Smirnov Test**: Statistical significance
- Per-feature and overall drift assessment

### 3. A/B Testing Framework
- Traffic splitting (percentage-based or user-based)
- Deterministic variant assignment
- Real-time performance comparison
- Automatic winner recommendation

### 4. Auto-Retraining Pipeline
- Performance threshold monitoring
- Drift-triggered retraining
- Training buffer management
- Version control and rollback

---

## Usage Examples

### Python Client Example
```python
import requests

BASE_URL = "http://localhost:5000/api/monitoring"

# Log a prediction
requests.post(f"{BASE_URL}/metrics/log", json={
    "model_name": "email_detector",
    "prediction": "phishing",
    "confidence": 0.95,
    "prediction_time": 0.123,
    "ground_truth": "phishing"
})

# Check for drift
response = requests.post(f"{BASE_URL}/drift/email_detector/check")
drift_report = response.json()

if drift_report['drift_report']['drift_detected']:
    print(f"⚠️ Drift detected! Severity: {drift_report['drift_report']['severity']}")

# Get metrics
response = requests.get(f"{BASE_URL}/metrics/email_detector")
metrics = response.json()
print(f"Accuracy: {metrics['metrics']['current']['accuracy']}")
```

### CURL Examples
```bash
# Get model metrics
curl http://localhost:5000/api/monitoring/metrics/email_detector

# Compare models
curl http://localhost:5000/api/monitoring/metrics/compare

# Check drift
curl -X POST http://localhost:5000/api/monitoring/drift/email_detector/check

# Get retraining status
curl http://localhost:5000/api/monitoring/retraining/email_detector/status

# Health check
curl http://localhost:5000/api/monitoring/health
```

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "status": "error",
  "message": "Detailed error message"
}
```

**HTTP Status Codes:**
- 200: Success
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

---

## Notes

- All timestamps are in UTC ISO 8601 format
- Metrics are calculated incrementally for performance
- Drift detection requires minimum 30 samples
- Retraining requires minimum 100 labeled samples
- A/B tests support deterministic user assignment for consistent experience
