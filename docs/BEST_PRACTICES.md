# Best Practices Guide

Unified Cyber Threat Detection System'ı en etkin ve güvenli şekilde kullanmak için önerilen uygulamalar.

---

## 1. Veri Hazırlığı

### Email Verisi

#### Önerilen Format
```python
import pandas as pd

email_data = pd.DataFrame({
    'email_text': [
        'Email body content here...',
        'Another email...'
    ],
    'sender': [
        'sender@example.com',
        'another@domain.com'
    ],
    'subject': [
        'Email Subject 1',
        'Email Subject 2'
    ]
})
```

#### Veri Temizliği
```python
def clean_email_data(email_text):
    """Email metnini temizle ve hazırla"""
    # Boşluğu kaldır
    email_text = email_text.strip()
    
    # Eksik veri kontrolü
    if not email_text or len(email_text) < 10:
        raise ValueError("Email metni çok kısa")
    
    # Çok uzun veriyi kesintiye uğrat
    if len(email_text) > 50000:
        email_text = email_text[:50000]
    
    return email_text

# Uygula
email_data['email_text'] = email_data['email_text'].apply(clean_email_data)
```

#### Veri Dengelemesi
```python
from sklearn.utils import resample

def balance_dataset(df, label_column='label'):
    """Dengesiz veri setini dengele"""
    # Sınıfları ayır
    majority = df[df[label_column] == 0]
    minority = df[df[label_column] == 1]
    
    # Azlık sınıfını örnekle
    if len(minority) < len(majority) * 0.3:
        minority = resample(
            minority,
            n_samples=len(majority) // 2,
            random_state=42
        )
    
    return pd.concat([majority, minority])

balanced_data = balance_dataset(email_data)
```

### Web Log Verisi

#### Log Format Doğrulaması
```python
import re

def validate_log_format(log_line):
    """Apache/Nginx log formatını doğrula"""
    # Apache Combined Log Format
    pattern = r'^(\S+) \S+ \S+ \[([\w:/]+\s[+\-]\d{4})\] "(\S+)\s?(\S+)?\s?(\S+)?" (\d{3}|-) (\d+|-)\s?"?([^"]*)"?\s?"?([^"]*)?"?$'
    
    return bool(re.match(pattern, log_line))

# Logları filtrele
valid_logs = [log for log in logs if validate_log_format(log)]
invalid_logs = [log for log in logs if not validate_log_format(log)]

print(f"Geçerli loglar: {len(valid_logs)}")
print(f"Geçersiz loglar: {len(invalid_logs)}")
```

---

## 2. Model Eğitimi

### Verileri Bölme

```python
from sklearn.model_selection import train_test_split, cross_val_score

def prepare_training_data(X, y, test_size=0.2, validation_size=0.1):
    """Eğitim verilerini ayır"""
    # Train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=42,
        stratify=y  # Sınıf dağılımını koru
    )
    
    # Train/validation
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train,
        test_size=validation_size,
        random_state=42,
        stratify=y_train
    )
    
    return X_train, X_val, X_test, y_train, y_val, y_test

X_train, X_val, X_test, y_train, y_val, y_test = prepare_training_data(
    emails['text'], emails['label']
)
```

### Hyperparameter Tuning

```python
from sklearn.model_selection import GridSearchCV

def tune_hyperparameters(X_train, y_train):
    """Best hyperparameters'ı bul"""
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [10, 20, 30],
        'min_samples_split': [2, 5, 10]
    }
    
    from sklearn.ensemble import RandomForestClassifier
    
    grid_search = GridSearchCV(
        RandomForestClassifier(),
        param_grid,
        cv=5,
        n_jobs=-1,
        verbose=1
    )
    
    grid_search.fit(X_train, y_train)
    
    print(f"Best params: {grid_search.best_params_}")
    print(f"Best score: {grid_search.best_score_:.4f}")
    
    return grid_search.best_estimator_

best_model = tune_hyperparameters(X_train, y_train)
```

### Cross-Validation

```python
from sklearn.model_selection import cross_validate

def validate_model(model, X, y):
    """Model performansını çapraz doğrula"""
    cv_results = cross_validate(
        model, X, y,
        cv=5,
        scoring=['accuracy', 'precision', 'recall', 'f1'],
        return_train_score=True
    )
    
    print("Cross-Validation Sonuçları:")
    for metric in ['accuracy', 'precision', 'recall', 'f1']:
        train_score = cv_results[f'train_{metric}'].mean()
        test_score = cv_results[f'test_{metric}'].mean()
        print(f"{metric}: train={train_score:.4f}, test={test_score:.4f}")
    
    return cv_results

validate_model(best_model, X_train, y_train)
```

---

## 3. Tahmin Yapma

### Batch Processing

```python
def predict_batch(detector, emails, batch_size=100):
    """Büyük veri setlerinde toplu tahmin yap"""
    results = []
    
    for i in range(0, len(emails), batch_size):
        batch = emails[i:i+batch_size]
        
        for email in batch:
            try:
                result = detector.predict_with_explanation(email)
                results.append(result)
            except Exception as e:
                print(f"Error processing email {i}: {e}")
                results.append({'error': str(e)})
    
    return results

# Kullan
all_predictions = predict_batch(detector, emails, batch_size=50)
```

### Error Handling

```python
from typing import Optional, Dict, Any

def safe_predict(detector, email_text: str) -> Optional[Dict[str, Any]]:
    """Hata yönetimi ile tahmin yap"""
    try:
        if not email_text or len(email_text) < 10:
            raise ValueError("Email too short")
        
        if len(email_text) > 50000:
            email_text = email_text[:50000]
        
        result = detector.predict_with_explanation(email_text)
        return result
        
    except ValueError as e:
        print(f"Input error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

---

## 4. Sonuçları Analiz Etme

### Confidence Thresholds

```python
def analyze_predictions(predictions, confidence_threshold=0.8):
    """Tahminleri confidence'a göre kategorize et"""
    high_confidence = []
    low_confidence = []
    
    for pred in predictions:
        if pred['confidence'] >= confidence_threshold:
            high_confidence.append(pred)
        else:
            low_confidence.append(pred)
    
    return high_confidence, low_confidence

high_conf, low_conf = analyze_predictions(results, confidence_threshold=0.85)

print(f"Yüksek güven: {len(high_conf)}")
print(f"Düşük güven: {len(low_conf)}")
```

### Risk Scoring

```python
def calculate_risk_distribution(predictions):
    """Risk skoru dağılımını hesapla"""
    import numpy as np
    
    risk_scores = [p['risk_score'] for p in predictions]
    
    stats = {
        'min': np.min(risk_scores),
        'max': np.max(risk_scores),
        'mean': np.mean(risk_scores),
        'median': np.median(risk_scores),
        'std': np.std(risk_scores)
    }
    
    return stats

risk_stats = calculate_risk_distribution(results)
print(f"Risk Skoru - Ort: {risk_stats['mean']:.1f}, Std: {risk_stats['std']:.1f}")
```

---

## 5. Performans Optimizasyonu

### Caching

```python
from functools import lru_cache
import hashlib

class CachedDetector:
    def __init__(self, detector):
        self.detector = detector
        self.cache = {}
    
    def _get_cache_key(self, email_text):
        return hashlib.md5(email_text.encode()).hexdigest()
    
    def predict_with_cache(self, email_text):
        cache_key = self._get_cache_key(email_text)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = self.detector.predict_with_explanation(email_text)
        self.cache[cache_key] = result
        
        return result
    
    def clear_cache(self):
        self.cache.clear()

cached_detector = CachedDetector(detector)
result = cached_detector.predict_with_cache(email_text)
```

### Parallel Processing

```python
from multiprocessing import Pool
from functools import partial

def parallel_predict(detector, emails, num_workers=4):
    """Paralel tahmin"""
    predict_func = partial(
        detector.predict_with_explanation
    )
    
    with Pool(num_workers) as pool:
        results = pool.map(predict_func, emails)
    
    return results

# Kullan
results = parallel_predict(detector, emails, num_workers=4)
```

---

## 6. Logging ve Monitoring

### Structured Logging

```python
import logging
from datetime import datetime

def setup_logging(log_file='threat_detection.log'):
    """Yapılandırılmış logging ayarla"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

logger = setup_logging()

# Kullan
logger.info(f"Analysis started for {len(emails)} emails")
logger.warning(f"Confidence below threshold: {low_conf_count}")
logger.error(f"Failed to process email: {error_message}")
```

### Performance Metrics

```python
import time
from statistics import mean, stdev

class PerformanceMonitor:
    def __init__(self):
        self.times = []
    
    def track(self, func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            self.times.append(elapsed)
            return result
        return wrapper
    
    def report(self):
        if not self.times:
            return
        
        print(f"Total calls: {len(self.times)}")
        print(f"Avg time: {mean(self.times):.4f}s")
        print(f"Min time: {min(self.times):.4f}s")
        print(f"Max time: {max(self.times):.4f}s")
        if len(self.times) > 1:
            print(f"Std dev: {stdev(self.times):.4f}s")

monitor = PerformanceMonitor()

@monitor.track
def predict(detector, email):
    return detector.predict_with_explanation(email)

monitor.report()
```

---

## 7. Güvenlik

### Input Validation

```python
def validate_input(email_text: str) -> bool:
    """Giriş doğrula"""
    if not email_text:
        return False
    
    if not isinstance(email_text, str):
        return False
    
    if len(email_text) < 10:
        return False
    
    if len(email_text) > 50000:
        return False
    
    # Zararlı karakterleri kontrol et
    dangerous_chars = ['<script>', 'eval(', 'exec(']
    for char in dangerous_chars:
        if char in email_text:
            return False
    
    return True
```

### Model Integrity

```python
import hashlib

def verify_model_integrity(model_path, expected_hash):
    """Model bütünlüğünü doğrula"""
    with open(model_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    
    if file_hash != expected_hash:
        raise ValueError("Model dosyası değiştirilmiş olabilir!")
    
    return True

# Kullan
verify_model_integrity('detector.pkl', 'expected_sha256_hash')
```

---

## 8. Documentation ve Versioning

### Model Documentation

```python
class ModelMetadata:
    def __init__(self, model_name, version, training_data, accuracy):
        self.model_name = model_name
        self.version = version
        self.training_data = training_data
        self.accuracy = accuracy
        self.created_at = datetime.now()
    
    def save_metadata(self, path):
        import json
        
        metadata = {
            'model_name': self.model_name,
            'version': self.version,
            'training_data': self.training_data,
            'accuracy': self.accuracy,
            'created_at': str(self.created_at)
        }
        
        with open(path, 'w') as f:
            json.dump(metadata, f, indent=2)
```

### Version Control

```bash
# Model versioning
model_v1.0.0.pkl  # ilk sürüm
model_v1.0.1.pkl  # bug fix
model_v1.1.0.pkl  # yeni özellikler
model_v2.0.0.pkl  # breaking changes
```

---

## 9. Deployment Checklist

- [ ] Veri temizliğini doğrula
- [ ] Model performansını test et (>85% accuracy)
- [ ] Hata yönetimini kontrol et
- [ ] Logging yapılandırmasını doğrula
- [ ] Güvenlik taramasını yap
- [ ] API documentation'u güncelle
- [ ] Load test'ini çalıştır
- [ ] Backup stratejisini hazırla
- [ ] Monitoring dashboard'u kur
- [ ] Operasyon ekibini eğit

---

## 10. Troubleshooting

### Model Düşük Performans
```python
# Kontrolü ve iyileştirmeler
- Veri kalitesini kontrol et
- Veri dengesizliğini gider
- Hyperparameters'ı ayarla
- Daha fazla eğitim verisi topla
```

### Yavaş Tahmin
```python
# Hızlandırma yöntemleri
- Batch processing kullan
- Paralel işlem yap
- Caching ekle
- GPU kullan
```

### Memory Hatası
```python
# Bellek azaltma
- Veri boyutunu azalt
- Chunk işleme yap
- Model boyutunu küçült
```

---

## Kaynaklar

- [API Documentation](api.html)
- [Architecture Guide](architecture.html)
- [Usage Examples](USAGE_SCENARIOS.md)
- [GitHub Repository](https://github.com/TheLastKhan/UnifiedCyberThreatDetectionSystem)
