# 🛡️ CyberGuard - Unified Cyber Threat Detection Platform

[![Production Ready](https://img.shields.io/badge/status-production--ready-brightgreen)](docs/DEPLOYMENT_GUIDE.md)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](requirements.txt)
[![Docker](https://img.shields.io/badge/docker-6%20containers-blue)](#docker-deployment)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> **Yapay zeka destekli kurumsal siber tehdit tespit platformu.** E-posta phishing tespiti ve web log analizi yaparak koordineli saldırıları gerçek zamanlı olarak tespit eder.

---

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Ekran Görüntüleri](#-ekran-görüntüleri)
- [Hızlı Başlangıç](#-hızlı-başlangıç)
- [Sistem Mimarisi](#-sistem-mimarisi)
- [Yapay Zeka Modelleri](#-yapay-zeka-modelleri)
- [API Referansı](#-api-referansı)
- [Dashboard Kullanımı](#-dashboard-kullanımı)
- [Konfigürasyon](#-konfigürasyon)
- [Geliştirme](#-geliştirme)
- [Lisans](#-lisans)

---

## ✨ Özellikler

### 🎯 Temel Yetenekler

| Özellik | Açıklama | Teknoloji |
|---------|----------|-----------|
| 📧 **E-posta Phishing Tespiti** | Üç farklı AI modeli ile phishing e-postalarını tespit eder | BERT, FastText, TF-IDF |
| 🌐 **Web Log Analizi** | SQL Injection, XSS, DDoS saldırılarını tespit eder | Isolation Forest |
| 🔗 **Korelasyon Analizi** | E-posta ve web tehditlerini ilişkilendirerek koordineli saldırıları bulur | Pearson Correlation |
| 📊 **Gerçek Zamanlı Dashboard** | İnteraktif grafikler ve anlık istatistikler | Chart.js |
| 🌍 **Çoklu Dil Desteği** | Türkçe ve İngilizce arayüz | i18next |
| 🌙 **Tema Desteği** | Karanlık ve aydınlık mod, tercih kalıcı olarak kaydedilir | CSS + LocalStorage + API |
| 📥 **Import/Export** | Excel ve JSON formatında veri aktarımı | pandas, openpyxl |
| 🐳 **Docker Deployment** | 6 container ile hazır dağıtım | Docker Compose |

### 📈 Performans Metrikleri

| Model | Doğruluk | Hız | Kullanım Alanı |
|-------|----------|-----|----------------|
| **BERT (DistilBERT)** | %94-97 | ~45ms | Yüksek doğruluk gereken durumlar |
| **FastText** | %90-94 | <1ms | Yüksek hacimli gerçek zamanlı işleme |
| **TF-IDF + Random Forest** | %89.75 | ~25ms | Açıklanabilir sonuçlar |
| **Isolation Forest** | %92+ | ~15ms | Web anomali tespiti |

---

## 📸 Ekran Görüntüleri

### Ana Dashboard
<img src="docs/professor_report/screenshots/01_dashboard.png" alt="Dashboard" width="800"/>

Dashboard, sistemin merkezi kontrol panelidir:
- **İstatistik Kartları:** E-posta analizi, Web anomali, Toplam tehdit, Sistem durumu
- **Tehdit Dağılımı:** Donut chart ile görsel tehdit dağılımı
- **Model Performans:** Bar chart ile model karşılaştırması
- **Son Uyarılar:** En güncel tehdit bildirimleri

### E-posta Analizi
<img src="docs/professor_report/screenshots/02_email_analysis.png" alt="Email Analysis" width="800"/>

- Üç model aynı anda analiz yapar (BERT, FastText, TF-IDF)
- Her model için ayrı güven skoru ve risk seviyesi
- Öne çıkan özellikler ve LIME açıklamaları

### Web Log Analizi
<img src="docs/professor_report/screenshots/03_web_analysis.png" alt="Web Analysis" width="800"/>

- IP adresi, HTTP method, path, status code, user-agent girişi
- Isolation Forest ile anomali tespiti
- SQL Injection, XSS, Bot activity tespiti

### Korelasyon Analizi
<img src="docs/professor_report/screenshots/04_correlation_analysis.png" alt="Correlation" width="800"/>

- E-posta ve web tehditlerinin zaman ve IP bazlı ilişkilendirilmesi
- Koordineli saldırı tespiti
- Korelasyon heatmap ve timeline grafikleri

### Model Karşılaştırma
<img src="docs/professor_report/screenshots/05_model_comparison.png" alt="Model Comparison" width="800"/>

- Accuracy, Precision, Recall, F1-Score karşılaştırması
- Model bazlı performans grafikleri

---

## 🚀 Hızlı Başlangıç

### Gereksinimler

| Bileşen | Minimum | Önerilen |
|---------|---------|----------|
| **İşletim Sistemi** | Windows 10, Linux, macOS | - |
| **Python** | 3.8 | 3.10+ |
| **RAM** | 4GB | 8GB |
| **Disk** | 2GB | 5GB |
| **Docker** | 20.10+ | 24.0+ |

### 🐳 Docker ile Kurulum (Önerilen)

```bash
# 1. Projeyi klonlayın
git clone https://github.com/TheLastKhan/UnifiedCyberThreatDetectionSystem.git
cd UnifiedCyberThreatDetectionSystem

# 2. Docker container'ları başlatın
docker-compose up -d

# 3. Durumu kontrol edin
docker-compose ps

# 4. Dashboard'a erişin
# http://localhost:5000
```

### Servis Erişim Noktaları

| Servis | URL | Kimlik Bilgileri |
|--------|-----|------------------|
| **Web Dashboard** | http://localhost:5000 | - |
| **Grafana** | http://localhost:3000 | admin / admin |
| **Prometheus** | http://localhost:9090 | - |
| **PostgreSQL** | localhost:5432 | postgres / postgres |
| **Redis** | localhost:6379 | - |

### 💻 Manuel Kurulum

```bash
# 1. Virtual environment oluşturun
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 3. Dashboard'u başlatın
python run_dashboard.py

# 4. Tarayıcıda açın
# http://localhost:5000
```

---

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         KULLANICI ARAYÜZÜ                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │  Dashboard  │ │   Email     │ │   Web Log   │ │    Raporlar     │   │
│  │   Paneli    │ │   Analizi   │ │   Analizi   │ │   & Ayarlar     │   │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └────────┬────────┘   │
└─────────┼───────────────┼───────────────┼─────────────────┼────────────┘
          │               │               │                 │
          └───────────────┼───────────────┼─────────────────┘
                          ▼               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          FLASK REST API                                  │
│  /api/email/*  │  /api/predict/*  │  /api/correlation/*  │  /api/*     │
└─────────────────────────────────────────────────────────────────────────┘
                          │               │
          ┌───────────────┼───────────────┼───────────────┐
          ▼               ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│    BERT     │  │  FastText   │  │  TF-IDF+RF  │  │  Isolation  │
│ (DistilBERT)│  │   Model     │  │   Model     │  │   Forest    │
│   %94-97    │  │   %90-94    │  │   %89.75    │  │    %92+     │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
                          │               │
                          ▼               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          VERİ KATMANI                                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │ PostgreSQL │  │   Redis    │  │ Prometheus │  │  Grafana   │        │
│  │ (Veritabanı)│  │  (Cache)   │  │ (Metrikler)│  │ (Dashboard)│        │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘        │
└─────────────────────────────────────────────────────────────────────────┘
```

### Docker Container Yapısı

| Container | Port | İşlev | Teknoloji |
|-----------|------|-------|-----------|
| `threat-detection-api` | 5000 | Ana API + ML Modelleri | Flask, Gunicorn |
| `threat-db` | 5432 | Veritabanı | PostgreSQL 15 |
| `cache` | 6379 | Önbellek | Redis 7 |
| `nginx` | 80, 443 | Reverse Proxy | Nginx |
| `prometheus` | 9090 | Metrik Toplama | Prometheus |
| `grafana` | 3000 | Görselleştirme | Grafana |

---

## 🤖 Yapay Zeka Modelleri

### 1. BERT (DistilBERT)

```python
# Kullanım
POST /api/email/analyze/bert
{
    "subject": "URGENT: Verify your account now!",
    "sender": "security@bank-fake.com",
    "body": "Click here to verify your account immediately..."
}
```

- **Mimari:** Transformer tabanlı, bidirectional encoder
- **Eğitim Verisi:** 31,000+ e-posta
- **Doğruluk:** %94-97
- **Avantaj:** Bağlamsal anlam çıkarımı

### 2. FastText

```python
# Kullanım
POST /api/email/analyze/fasttext
{
    "body": "You have won $1,000,000! Click here to claim..."
}
```

- **Mimari:** Word embedding + Linear classifier
- **Model Boyutu:** 881 MB
- **Doğruluk:** %90-94
- **Avantaj:** Çok hızlı (<1ms)

### 3. TF-IDF + Random Forest

```python
# Kullanım
POST /api/email/analyze
{
    "subject": "Meeting tomorrow",
    "sender": "colleague@company.com",
    "body": "Hi, let's meet tomorrow at 3pm."
}
```

- **Mimari:** TF-IDF vektörizasyon + Random Forest ensemble
- **Doğruluk:** %89.75
- **ROC-AUC:** %97.50
- **Avantaj:** Açıklanabilir sonuçlar

### 4. Isolation Forest (Web Analizi)

```python
# Kullanım
POST /api/predict/web
{
    "ip": "45.142.212.61",
    "method": "POST",
    "path": "/admin/login",
    "status": 401,
    "user_agent": "sqlmap/1.0"
}
```

- **Mimari:** Isolation Forest anomali tespiti
- **Tespit:** SQL Injection, XSS, DDoS, Bot traffic

---

## 📡 API Referansı

### Sağlık Kontrolü

```bash
GET /api/health
# Response: {"status": "healthy", "version": "1.0.0"}
```

### E-posta Analizi

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/api/email/analyze` | POST | TF-IDF ile analiz |
| `/api/email/analyze/bert` | POST | BERT ile analiz |
| `/api/email/analyze/fasttext` | POST | FastText ile analiz |
| `/api/email/analyze/hybrid` | POST | Tüm modeller ile analiz |

### Web Log Analizi

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/api/predict/web` | POST | Web log anomali analizi |

### Korelasyon

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/api/correlation/analyze` | GET | Tehdit korelasyonu |

### Dashboard

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/api/dashboard/stats` | GET | İstatistikler |
| `/api/models/status` | GET | Model durumları |

### Raporlar

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/api/reports/export/excel` | GET | Excel dışa aktarma |
| `/api/reports/export/json` | GET | JSON dışa aktarma |

### Ayarlar

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/api/settings` | GET | Ayarları getir |
| `/api/settings` | POST | Ayarları kaydet |

### Demo & Yönetim

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/api/demo/generate` | POST | Demo veri oluştur |
| `/api/database/clear` | POST | Verileri temizle |

---

## 🖥️ Dashboard Kullanımı

### Navigasyon

| Sayfa | İşlev |
|-------|-------|
| **Dashboard** | Genel durum ve istatistikler |
| **Email Analysis** | E-posta phishing analizi |
| **Web Analysis** | Web log anomali analizi |
| **Correlation Analysis** | Tehdit korelasyonu |
| **Model Comparison** | Model performans karşılaştırması |
| **Reports** | Dışa/İçe aktarma |
| **Settings** | Sistem ayarları |

### Üst Menü Butonları

| Buton | İşlev |
|-------|-------|
| **Generate Demo Data** | Test için örnek veri oluşturur |
| **Clear History** | Tüm verileri siler |
| **☀/🌙 (Tema)** | Aydınlık/Karanlık mod değiştirir |
| **TR/EN (Dil)** | Arayüz dilini değiştirir |

### Tema ve Dil Kalıcılığı

- Tema ve dil tercihleri hem `localStorage`'a hem de veritabanına kaydedilir
- Tarayıcı kapatılıp açılsa bile tercihler korunur
- Varsayılan tema: Aydınlık mod

---

## ⚙️ Konfigürasyon

### Ortam Değişkenleri

```bash
# .env dosyası oluşturun
DATABASE_URL=postgresql://postgres:postgres@db:5432/threat_detection
REDIS_URL=redis://cache:6379/0
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
LOG_LEVEL=INFO

# Opsiyonel
VIRUSTOTAL_API_KEY=your_api_key_here
```

### Ayarlar Sayfası

| Ayar | Tür | Açıklama |
|------|-----|----------|
| **Dark Mode** | Toggle | Karanlık tema |
| **Language** | Checkbox | Türkçe/İngilizce |
| **Detection Threshold** | Slider | Phishing eşiği (0.0-1.0) |
| **High Risk Alerts** | Toggle | Yüksek risk bildirimi |
| **Daily Reports** | Toggle | Günlük özet rapor |

---

## 🛠️ Geliştirme

### Proje Yapısı

```
UnifiedCyberThreatDetectionSystem/
├── web_dashboard/           # Web arayüzü
│   ├── api.py              # Flask API endpoints
│   ├── static/             # CSS, JS dosyaları
│   └── templates/          # HTML şablonları
├── src/
│   ├── email_detector/     # E-posta modelleri
│   ├── web_analyzer/       # Web log analizi
│   └── unified_platform/   # Korelasyon
├── models/                 # Eğitilmiş modeller
├── training/               # Model eğitim scriptleri
├── tests/                  # Test dosyaları
├── docs/                   # Dokümantasyon
│   └── professor_report/   # Proje raporu ve ekran görüntüleri
├── docker-compose.yml      # Docker konfigürasyonu
└── requirements.txt        # Python bağımlılıkları
```

### Test Çalıştırma

```bash
# Tüm testleri çalıştır
pytest tests/ -v

# Belirli bir test dosyasını çalıştır
pytest tests/test_api.py -v
```

### API Geliştirme

```bash
# Development modda çalıştır
python run_dashboard.py

# veya
flask run --debug
```

---

## 📄 Dokümantasyon

| Dosya | İçerik |
|-------|--------|
| [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) | Dağıtım rehberi |
| [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) | API detayları |
| [ADVANCED_NLP_INTEGRATION.md](docs/ADVANCED_NLP_INTEGRATION.md) | NLP modelleri |
| [professor_report/](docs/professor_report/) | Proje raporu ve ekran görüntüleri |

---

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 🙏 Teşekkürler

- CEAS 2008 Dataset - E-posta eğitim verisi
- Enron Email Dataset - Model validasyonu
- Hugging Face - Transformers kütüphanesi
- Facebook Research - FastText

---

## 📧 İletişim

- **GitHub:** [TheLastKhan](https://github.com/TheLastKhan)
- **Proje:** [UnifiedCyberThreatDetectionSystem](https://github.com/TheLastKhan/UnifiedCyberThreatDetectionSystem)

---

**⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!**
