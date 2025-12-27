# Usage Examples & Real-World Scenarios

Unified Cyber Threat Detection System'i gerçek dünya senaryolarında nasıl kullanacağınızı öğrenin.

---

## Senaryo 1: Phishing Campaign Detection

### Kurum Senaryosu
Bir şirketin HR departmanına benzer phishing emailler gelmeye başladı. Sistem yöneticisi, bu emailleri toplu olarak kontrol etmek istemelidir.

### İşlem Adımları

#### Adım 1: Emaillerinizi Toplayın
```python
import pandas as pd
from src.email_detector import EmailDetector

# CSV dosyasından emaillerinizi okuyun
emails_df = pd.read_csv('suspicious_emails.csv')
# Sütunlar: email_text, sender, subject

print(f"Toplam {len(emails_df)} email analiz edilecek")
```

#### Adım 2: Detector'u Başlatın
```python
detector = EmailDetector()

# Önceden eğitilmiş modeli yükleyin
detector.load_model('path/to/trained_model')
```

#### Adım 3: Toplu Analiz Yapın
```python
results = []

for idx, row in emails_df.iterrows():
    prediction = detector.predict_with_explanation(
        email_text=row['email_text'],
        sender=row['sender'],
        subject=row['subject']
    )
    
    results.append({
        'email_id': idx,
        'sender': row['sender'],
        'subject': row['subject'],
        'is_phishing': prediction['prediction'],
        'confidence': prediction['confidence'],
        'risk_score': prediction['risk_score'],
        'risk_factors': prediction['risk_factors']
    })

results_df = pd.DataFrame(results)
print(results_df.to_string())
```

#### Adım 4: Sonuçları Analiz Edin
```python
# Phishing olasılığı yüksek emailler
phishing_emails = results_df[results_df['confidence'] > 0.8]
print(f"\nYüksek risk: {len(phishing_emails)} email")

# Risk faktörlerini görüntüle
for idx, email in phishing_emails.iterrows():
    print(f"\n--- Email #{email['email_id']} ---")
    print(f"From: {email['sender']}")
    print(f"Subject: {email['subject']}")
    print(f"Risk Score: {email['risk_score']:.0f}/100")
    
    for factor in email['risk_factors']:
        print(f"  - {factor['factor']}: {factor['evidence']}")
```

#### Adım 5: Rapor Oluşturun
```python
# Riskli emailler CSV olarak kaydet
phishing_emails.to_csv('phishing_emails_report.csv', index=False)

# Özet rapor
summary = {
    'total_emails': len(results_df),
    'phishing_count': len(phishing_emails),
    'phishing_percentage': (len(phishing_emails) / len(results_df)) * 100,
    'average_risk_score': results_df['risk_score'].mean()
}

print("\n=== ÖZET RAPOR ===")
print(f"Toplam Email: {summary['total_emails']}")
print(f"Phishing Sayısı: {summary['phishing_count']}")
print(f"Phishing Yüzdesi: {summary['phishing_percentage']:.1f}%")
print(f"Ortalama Risk Skoru: {summary['average_risk_score']:.1f}")
```

---

## Senaryo 2: Web Server Attack Detection

### Kurum Senaryosu
Bir web sunucusu anormal traffic gösteriyor. Saldırı desenleri ve anomalileri tespit etmek istiyorsunuz.

### İşlem Adımları

#### Adım 1: Web Loglarını Alın
```python
from src.web_analyzer import WebAnalyzer

# Apache/Nginx log dosyasını okuyun
with open('access.log', 'r') as f:
    logs = f.readlines()

print(f"Toplam {len(logs)} log satırı analiz edilecek")
```

#### Adım 2: Analyzer'i Başlatın ve Eğitin
```python
analyzer = WebAnalyzer()

# Normal traffic ile eğitin (training data)
normal_logs = logs[:1000]  # İlk 1000 satır normal olduğu varsayılıyor
analyzer.train_anomaly_detector(normal_logs)

print("Analyzer eğitildi")
```

#### Adım 3: Anomali Tespiti Yapın
```python
# Tüm logları analiz et
analysis_results = analyzer.analyze_ip_with_explanation(logs)

print(f"Toplam anomali tespit edildi: {analysis_results['anomalies_detected']}")
```

#### Adım 4: Risk IP'lerini Belirleyin
```python
import pandas as pd

anomaly_scores = analysis_results['anomaly_scores']
anomaly_df = pd.DataFrame(anomaly_scores)

# Yüksek risk IP'ler
high_risk_ips = anomaly_df[anomaly_df['anomaly_score'] > 0.7]

print("\n=== YÜKSEK RİSK IP'LERİ ===")
for idx, row in high_risk_ips.iterrows():
    print(f"\nIP: {row['ip_address']}")
    print(f"Anomali Skoru: {row['anomaly_score']:.2f}")
    print(f"Risk Seviyesi: {row['risk_level']}")
    print(f"İndikatörler: {', '.join(row['indicators'])}")
```

#### Adım 5: Güvenlik Önlemleri Alın
```python
# Firewall bloklama listesi oluştur
high_risk_ips_list = high_risk_ips['ip_address'].unique().tolist()

# Firewall kuralı oluştur (örnek)
firewall_rules = []
for ip in high_risk_ips_list:
    firewall_rules.append(f"iptables -I INPUT -s {ip} -j DROP")

# Dosyaya kaydet
with open('firewall_rules.sh', 'w') as f:
    for rule in firewall_rules:
        f.write(rule + '\n')

print(f"{len(firewall_rules)} IP adresi bloke edildi")
```

---

## Senaryo 3: Coordinated Attack Detection

### Kurum Senaryosu
Phishing emaili alan kullanıcılar aynı anda web sunucusuna anormal erişim gösteriyor. Cross-platform korelasyon gerekli.

### İşlem Adımları

#### Adım 1: Email ve Web Verilerini Hazırlayın
```python
from src.unified_platform import UnifiedPlatform

# Email verisi
email_data = {
    "text": "Urgent: Verify your credentials now! Click here...",
    "sender": "admin@fake-company.com",
    "subject": "Security Alert"
}

# Web log verisi
web_logs = [
    '192.168.1.100 - - [08/Dec/2024:10:30:00 +0000] "POST /admin/login HTTP/1.1" 401 0',
    '192.168.1.100 - - [08/Dec/2024:10:30:05 +0000] "POST /admin/login HTTP/1.1" 401 0',
    '192.168.1.100 - - [08/Dec/2024:10:30:10 +0000] "GET /admin HTTP/1.1" 403 0'
]
```

#### Adım 2: Unified Platform'u Başlatın
```python
platform = UnifiedPlatform()
platform.initialize()

print("Unified Platform başlatıldı")
```

#### Adım 3: Unified Analiz Yapın
```python
threat_analysis = platform.analyze_unified_threat(
    email_data=email_data,
    web_logs=web_logs
)

print(f"Threat ID: {threat_analysis['threat_id']}")
print(f"Genel Risk Skoru: {threat_analysis['overall_risk_score']:.0f}/100")
print(f"Genel Risk Seviyesi: {threat_analysis['overall_risk_level']}")
```

#### Adım 4: Korelasyonu Analiz Edin
```python
print("\n=== KORELASYONLAR ===")
print(f"Korelasyon Skoru: {threat_analysis['correlation_score']:.2f}")

print("\nBağlantılı Tehditler:")
for correlation in threat_analysis['correlated_threats']:
    print(f"  Email: {correlation['email_risk_factor']}")
    print(f"  Web: {correlation['web_indicator']}")
    print(f"  Kuvveti: {correlation['correlation_strength']:.2f}")
```

#### Adım 5: Öneriler Uygulayın
```python
print("\n=== GÜVENLİK ÖNERİLERİ ===")
for i, recommendation in enumerate(threat_analysis['recommendations'], 1):
    print(f"{i}. {recommendation}")

# Otomatik tepki
if threat_analysis['overall_risk_level'] == 'critical':
    # Email quarantine
    print("\n[OTOMATIK İŞLEM]")
    print("- Email karantinaya alındı")
    
    # IP bloklama
    attacker_ip = '192.168.1.100'
    print(f"- IP {attacker_ip} firewall'da bloklandi")
    
    # Alert gönder
    print("- Güvenlik ekibine alert gönderildi")
```

---

## Senaryo 4: Model Eğitimi ve Geliştirme

### Kurum Senaryosu
Yeni phishing türleri ortaya çıktı. Modelinizi kendi verilerinizle eğitmek istiyorsunuz.

### İşlem Adımları

#### Adım 1: Eğitim Verisi Hazırlayın
```python
import pandas as pd
from src.email_detector import EmailDetector

# CSV formatında eğitim verisi
training_data = pd.read_csv('training_data.csv')
# Sütunlar: email_text (string), label (0=meşru, 1=phishing)

print(f"Meşru email: {(training_data['label'] == 0).sum()}")
print(f"Phishing email: {(training_data['label'] == 1).sum()}")
```

#### Adım 2: Veri Dengesizliğini Kontrol Edin
```python
# Dengesizlik durumunda oversampling yapın
from sklearn.utils import resample

phishing_emails = training_data[training_data['label'] == 1]
legitimate_emails = training_data[training_data['label'] == 0]

if len(phishing_emails) < len(legitimate_emails) * 0.3:
    # Phishing emaillerini kopyala
    phishing_resampled = resample(
        phishing_emails,
        n_samples=len(legitimate_emails) // 2,
        random_state=42
    )
    training_data = pd.concat([legitimate_emails, phishing_resampled])

print(f"Dengeli veri: {len(training_data)} örnek")
```

#### Adım 3: Modeli Eğitin
```python
detector = EmailDetector()

# Modeli eğit
trained_model = detector.train(
    emails_df=training_data,
    labels=training_data['label'].tolist()
)

print("Model eğitimi tamamlandı")
```

#### Adım 4: Performansı Değerlendirin
```python
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# Test seti oluştur
X_train, X_test, y_train, y_test = train_test_split(
    training_data['email_text'],
    training_data['label'],
    test_size=0.2,
    random_state=42
)

# Tahmin yap
y_pred = detector.predict_batch(X_test.tolist())

# Rapor
print("\n=== KLASİFİKASYON RAPORU ===")
print(classification_report(y_test, y_pred))

# Confusion matrix
print("\n=== CONFUSION MATRIX ===")
cm = confusion_matrix(y_test, y_pred)
print(cm)
```

#### Adım 5: Modeli Kaydedin
```python
# Model dosyasını kaydet
detector.save_model('custom_email_detector.pkl')

print("Model kaydedildi: custom_email_detector.pkl")
```

---

## Senaryo 5: Dashboard Integration

### Kurum Senaryosu
Threat analiz sonuçlarını web dashboard'da görüntülemek istiyorsunuz.

### İşlem Adımları

#### Adım 1: Flask Uygulamasını Başlatın
```python
from flask import Flask, jsonify, request
from src.unified_platform import UnifiedPlatform

app = Flask(__name__)
platform = UnifiedPlatform()
platform.initialize()

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    
    result = platform.analyze_unified_threat(
        email_data=data.get('email'),
        web_logs=data.get('web_logs', [])
    )
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

#### Adım 2: Dashboard HTML Oluşturun
```html
<!DOCTYPE html>
<html>
<head>
    <title>Threat Detection Dashboard</title>
    <style>
        .risk-critical { color: red; font-weight: bold; }
        .risk-high { color: orange; font-weight: bold; }
        .risk-medium { color: yellow; }
        .risk-low { color: green; }
    </style>
</head>
<body>
    <h1>Unified Threat Detection Dashboard</h1>
    
    <div id="results"></div>
    
    <script>
        async function analyzeThreat() {
            const emailText = document.getElementById('emailText').value;
            const webLogs = document.getElementById('webLogs').value.split('\n');
            
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: { text: emailText },
                    web_logs: webLogs
                })
            });
            
            const result = await response.json();
            displayResults(result);
        }
        
        function displayResults(result) {
            const html = `
                <h2>Analysis Result</h2>
                <p class="risk-${result.overall_risk_level}">
                    Risk Level: ${result.overall_risk_level.toUpperCase()}
                </p>
                <p>Risk Score: ${result.overall_risk_score}/100</p>
            `;
            
            document.getElementById('results').innerHTML = html;
        }
    </script>
</body>
</html>
```

---

## Best Practices

### 1. Error Handling
```python
from src.email_detector import EmailDetector

try:
    detector = EmailDetector()
    result = detector.predict_with_explanation(email_text)
except ValueError as e:
    print(f"Giriş hatası: {e}")
except Exception as e:
    print(f"Beklenmeyen hata: {e}")
```

### 2. Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Analiz başladı")
logger.error("Analiz sırasında hata oluştu")
```

### 3. Performance Optimization
```python
# Batch işleme
emails = [...]  # 10000+ email

batch_size = 100
for i in range(0, len(emails), batch_size):
    batch = emails[i:i+batch_size]
    results = detector.predict_batch(batch)
    # Process results
```

### 4. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def analyze_email_cached(email_text):
    return detector.predict_with_explanation(email_text)
```

---

## Troubleshooting

### Problem: Memory Error with Large Datasets
```python
# Solution: Process in chunks
def process_large_dataset(data, chunk_size=1000):
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        yield process_chunk(chunk)
```

### Problem: Slow Predictions
```python
# Solution: Use GPU if available
import torch

if torch.cuda.is_available():
    detector.model.cuda()
    print("GPU kullanılıyor")
```

### Problem: Model Not Found
```python
# Solution: Check path and download if needed
import os

model_path = 'models/detector.pkl'
if not os.path.exists(model_path):
    print("Model dosyası bulunamadı. İndiriliyor...")
    # Download from remote
```

---

## Next Steps

1. **Model Customization** - Kendi verilerinizle modeli eğitin
2. **API Integration** - Sistemlerinize entegre edin
3. **Monitoring** - Dashboard ile sürekli izleyin
4. **Alerting** - Otomatik uyarı sistemi kurun

---

## Daha Fazla Yardım

- API Docs: [docs/api.html](api.html)
- Architecture: [docs/architecture.html](architecture.html)
- GitHub Issues: [Project Issues](https://github.com/TheLastKhan/UnifiedCyberThreatDetectionSystem/issues)
