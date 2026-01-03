# 🛡️ CyberGuard: Unified Cyber Threat Detection System
## Proje Final Raporu

**Hazırlayan:** Proje Ekibi  
**Tarih:** 27 Aralık 2025 (Güncelleme: 3 Ocak 2026)  
**Versiyon:** 2.0.0

---

## 📋 İçindekiler
1. [Proje Özeti](#proje-özeti)
2. [Yazılım Mimarisi ve Tasarım](#yazılım-mimarisi-ve-tasarım)
3. [Mimari Kalıplar ve Tasarım Desenleri](#mimari-kalıplar-ve-tasarım-desenleri)
4. [Özellikler ve Ekran Görüntüleri](#özellikler-ve-ekran-görüntüleri)
5. [Teknik Detaylar](#teknik-detaylar)
6. [Test Metodolojisi ve Sonuçları](#test-metodolojisi-ve-sonuçları)
7. [Model Karşılaştırması ve Trade-off Analizi](#model-karşılaştırması-ve-trade-off-analizi)
8. [Kurulum ve Çalıştırma](#kurulum-ve-çalıştırma)

---

## 🎯 Proje Özeti

**CyberGuard**, yapay zeka destekli bir siber tehdit tespit platformudur. E-posta phishing tespiti ve web log analizi yaparak kurumsal güvenliği sağlar.

### Temel Özellikler

| Özellik | Açıklama | Durum |
|---------|----------|-------|
| 📧 E-posta Phishing Tespiti | 3 farklı AI modeli (BERT, FastText, TF-IDF) | ✅ Çalışıyor |
| 🌐 Web Log Analizi | SQL Injection, XSS, DDoS tespiti | ✅ Çalışıyor |
| 🔗 Korelasyon Analizi | E-posta ve web tehditlerini ilişkilendirme | ✅ Çalışıyor |
| 📊 Gerçek Zamanlı Dashboard | İnteraktif grafikler ve istatistikler | ✅ Çalışıyor |
| 🌍 Çoklu Dil Desteği | Türkçe / İngilizce | ✅ Çalışıyor |
| 🌙 Tema Desteği | Light / Dark Mode | ✅ Çalışıyor |
| 📥 Import/Export | Excel ve JSON formatı | ✅ Çalışıyor |
| 🐳 Docker Deployment | 6 container ile hazır dağıtım | ✅ Çalışıyor |

---

## 🏗️ Yazılım Mimarisi ve Tasarım

### Mimari Karakterizasyon

CyberGuard, **modüler, servis-odaklı bir mimari** üzerine inşa edilmiştir. Sistemin mimari karakteri şu şekilde tanımlanabilir:

> **"CyberGuard is designed as a modular, service-oriented architecture where the sensing logic and presentation layers are separated, which allows machine learning models to develop independently."**

#### Mimari Tipi: Request-Response + Event-Driven Hybrid

Sistem temel olarak **request-response** paradigmasını kullanmakla birlikte, tehdit tespiti ve korelasyon analizi bileşenlerinde **event-driven** yaklaşımı benimser:

| Bileşen | Paradigma | Açıklama |
|---------|-----------|----------|
| Dashboard → API | Request-Response | Kullanıcı istekleri synchronous olarak işlenir |
| Email/Web Log → Detection | Event-Driven | Gelen veriler event olarak işlenir, detection pipeline'ı tetiklenir |
| Detection → Correlation | Publisher-Subscriber | Tespit edilen tehditler korelasyon motoruna publish edilir |
| Correlation → Alerts | Event-Driven | Koordineli saldırılar algılandığında alert event'leri oluşturulur |

### Mimari Kararların Gerekçeleri

#### Neden Phishing ve Web Log Aynı Backend'de?

**Karar:** E-posta phishing tespiti ve web log analizi tek bir Flask API backend'inde birleştirilmiştir.

**Gerekçe:**
1. **Korelasyon Avantajı:** Aynı IP adresinden gelen phishing e-postası ve web saldırısı, paylaşımlı veri katmanı sayesinde hızlıca ilişkilendirilebilir
2. **Kaynak Verimliliği:** Tek container, düşük memory footprint (küçük/orta ölçekli kurumlar için ideal)
3. **Deployment Basitliği:** Tek docker image, kolay bakım ve güncelleme
4. **Veri Tutarlılığı:** Merkezi PostgreSQL veritabanı, tüm tehdit verileri için single source of truth

**Alternatif Değerlendirme:** Microservice mimarisine geçiş, yüksek ölçeklenebilirlik için düşünülebilir ancak mevcut kullanım senaryosu için overengineering olarak değerlendirilmiştir.

#### Neden Model Inference API İçinde?

**Karar:** ML modelleri (BERT, FastText, TF-IDF) doğrudan Flask API container'ı içinde çalıştırılmaktadır.

**Gerekçe:**
1. **Latency Optimizasyonu:** Model → API arası network hop'u elimine edilmiştir (~5-10ms tasarruf)
2. **Session State:** Modeller bir kez yüklenir ve memory'de tutulur (cold start yok)
3. **Debugging Kolaylığı:** End-to-end tracing tek process'te yapılabilir
4. **Resource Isolation:** Docker container zaten izolasyon sağlar

**Trade-off:** Bu yaklaşım horizontal scaling'i zorlaştırır. Yüksek throughput senaryolarında TensorFlow Serving veya TorchServe gibi dedicated inference server'lara geçiş önerilir.

### Katman Ayrımı ve Sorumluluklar

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER (View)                         │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Flask Dashboard (Jinja2 Templates + JavaScript + CSS)       │    │
│  │  - Kullanıcı etkileşimi, form handling, data visualization   │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼ HTTP Requests
┌─────────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER (Controller)                    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Flask REST API (Routes, Request Validation, Response Format)│    │
│  │  - /api/email/*, /api/predict/*, /api/correlation/*          │    │
│  │  - Business logic orchestration, input sanitization          │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼ Function Calls
┌─────────────────────────────────────────────────────────────────────┐
│                    DOMAIN LAYER (Model/Business Logic)               │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐            │
│  │  Email Detec. │  │  Web Analyzer │  │  Correlation  │            │
│  │  (BERT/FT/TF) │  │  (Isolation F)│  │  Engine       │            │
│  └───────────────┘  └───────────────┘  └───────────────┘            │
│  - ML inference, feature extraction, risk scoring                   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼ ORM Queries
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA LAYER (Persistence)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │ PostgreSQL  │  │    Redis    │  │ File System │                  │
│  │ (Predictions)│  │   (Cache)   │  │ (ML Models) │                  │
│  └─────────────┘  └─────────────┘  └─────────────┘                  │
│  - Data persistence, caching, model storage                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Mimari Kalıplar ve Tasarım Desenleri

CyberGuard sistemi, bilinen birçok mimari ve tasarım modelini örtük olarak benimser. Sistem açıkça tek bir model etrafında tasarlanmamış olsa da, modüler yapısı doğal olarak MVC ve olay odaklı prensiplerle uyumludur. Bu yaklaşım, sistemin **bakım kolaylığını**, **ölçeklenebilirliğini** ve **genişletilebilirliğini** artırır.

### Pattern-Mapping Tablosu

| Mimari Kalıp / Tasarım Deseni | CyberGuard'daki Karşılığı | Uygulama Detayı |
|-------------------------------|---------------------------|-----------------|
| **Model-View-Controller (MVC)** | Dashboard (View), Flask API (Controller), PostgreSQL + ML Models (Model) | Presentation logic tamamen Jinja2 templates ve JavaScript'te; business logic API routes'ta; data layer SQLAlchemy ORM ile |
| **Event-Driven / Publisher-Subscriber** | Email/Web log ingestion → Detection → Correlation → Alert | Yeni bir email analiz edildiğinde, sonuç otomatik olarak correlation engine'e "publish" edilir |
| **Ensemble Learning Pattern** | BERT, FastText ve TF-IDF sonuçlarının weighted voting ile birleştirilmesi | Her model bağımsız inference yapar, sonuçlar weight'lere göre combine edilir (BERT: 0.5, FastText: 0.3, TF-IDF: 0.2) |
| **Cache-Aside Pattern** | Redis ile sık erişilen dashboard istatistiklerinin cachelenmesi | Dashboard stats önce Redis'te aranır, miss durumunda DB'den çekilir ve cache'e yazılır (TTL: 60s) |
| **Repository Pattern** | SQLAlchemy ORM ile database abstraction | `database.py` modülü, tüm CRUD operasyonlarını soyutlar; business logic SQL bilmez |
| **Factory Pattern** | Model detector instance'larının lazy initialization | `get_bert_detector()`, `get_fasttext_detector()` fonksiyonları singleton-like instance döndürür |
| **Strategy Pattern** | Farklı ML modellerinin aynı interface üzerinden kullanımı | Tüm detectorlar `predict(text)` ve `predict_with_explanation(text)` metodlarını implement eder |
| **Façade Pattern** | `/api/email/analyze/hybrid` endpoint'i | 3 modeli tek endpoint arkasında gizler, client karmaşıklığı görmez |
| **Circuit Breaker Pattern** | VirusTotal API entegrasyonunda graceful degradation | VT API erişilemezse, sistem sadece ML-based detection ile çalışmaya devam eder |

### Kalıp Seçim Gerekçeleri

#### Neden MVC?
- Separation of concerns: Frontend geliştiricisi API'yi bilmeden UI değiştirebilir
- Testability: Controller logic unit test edilebilir
- Reusability: Aynı API farklı frontend'lerden kullanılabilir

#### Neden Ensemble Learning?
- Single point of failure yok: Bir model başarısız olsa diğerleri çalışır
- Accuracy boost: Ensemble genellikle tek modelden daha iyi performans
- Explainability: Hangi modelin nasıl karar verdiği görülebilir

#### Neden Cache-Aside?
- Dashboard yükleme hızı: ~1s → ~200ms improvement
- Database load reduction: Sık sorgular cache'ten karşılanır
- Simplicity: Daha karmaşık write-through veya write-behind pattern'lere gerek yok

---

## 📸 Özellikler ve Ekran Görüntüleri

### 1. Ana Dashboard

Dashboard, sistemin merkezi kontrol panelidir. Tüm tehditlerin özet görünümünü sağlar.

![Dashboard Görünümü](dashboard_initial_view_1766837683729.png)

**Özellikler:**
- 📊 **İstatistik Kartları:** Email analizi, Web anomali, Toplam tehdit, Sistem durumu
- 📈 **Tehdit Dağılımı Grafiği:** Donut chart ile görsel tehdit dağılımı
- 🚨 **Son Uyarılar:** En son tespit edilen tehditler
- 🎮 **Demo Data Butonu:** Test için örnek veri oluşturma
- 🗑️ **Clear History:** Tüm verileri temizleme

---

### 2. E-posta Phishing Analizi

Üç farklı AI modeli ile e-posta analizi yapılır ve sonuçlar karşılaştırmalı olarak gösterilir.

#### Phishing Tespiti Örneği:

![Phishing Tespiti](phishing_analysis_result_1766837787501.png)

**Test Girdisi:**
- **Konu:** "URGENT: Your account will be suspended"
- **Gönderen:** security@paypal-fake.com
- **İçerik:** "Click here immediately to verify your account..."

**Sonuç:** 🚨 **PHISHING** - Tüm 3 model doğru tespit etti!

---

#### Meşru E-posta Örneği:

![Meşru E-posta](legitimate_analysis_result_1766837823005.png)

**Test Girdisi:**
- **Konu:** "Meeting tomorrow at 3pm"
- **Gönderen:** colleague@company.com
- **İçerik:** "Hi, don't forget our meeting tomorrow..."

**Sonuç:** ✅ **LEGITIMATE** - Tüm 3 model doğru tespit etti!

---

### 3. Web Log Analizi

Web sunucu loglarını analiz ederek SQL Injection, XSS ve diğer saldırıları tespit eder.

#### Anomali Tespiti:

![Web Anomali](web_analysis_anomaly_test_1766837892660.png)

**Test Girdisi:**
- **IP:** 45.142.212.61
- **Method:** POST
- **Path:** /admin/login
- **Status:** 401
- **User-Agent:** sqlmap/1.0

**Sonuç:** 🚨 **ANOMALY DETECTED** - SQL Injection aracı tespit edildi!

---

### 4. Korelasyon Analizi

E-posta ve web tehditlerini ilişkilendirerek koordineli saldırıları tespit eder.

![Korelasyon Analizi](correlation_analysis_page_1766837944859.png)

**Özellikler:**
- 📊 **Korelasyon Skoru:** Pearson korelasyon hesaplama
- 🎯 **Koordineli Saldırılar:** Aynı IP'den gelen çoklu tehditler
- 📈 **Zaman Çizelgesi:** Saat bazında tehdit dağılımı
- 🔥 **Heatmap:** Korelasyon ısı haritası

---

## 🔧 Teknik Detaylar

### Kullanılan Teknolojiler

| Kategori | Teknoloji |
|----------|-----------|
| **Backend** | Python 3.8+, Flask, Gunicorn |
| **Frontend** | HTML5, CSS3, JavaScript, Chart.js |
| **Machine Learning** | scikit-learn, PyTorch, Transformers |
| **NLP** | BERT (DistilBERT), FastText, TF-IDF |
| **Database** | PostgreSQL 15, SQLAlchemy ORM |
| **Cache** | Redis 7 |
| **Deployment** | Docker, Docker Compose, Nginx |
| **Monitoring** | Prometheus, Grafana |

### Docker Container Yapısı

| Container | Port | Açıklama |
|-----------|------|----------|
| `threat-detection-api` | 5000 | Flask API + ML Modelleri |
| `threat-db` | 5432 | PostgreSQL Veritabanı |
| `cache` | 6379 | Redis Cache |
| `nginx` | 80/443 | Reverse Proxy |
| `prometheus` | 9090 | Metrik Toplama |
| `grafana` | 3000 | Dashboard |

---

## 🧪 Test Metodolojisi ve Sonuçları

### Test Stratejisi ve Amacı

CyberGuard için tasarlanan test stratejisi, sistemin **temel güvenlik fonksiyonlarının doğruluğunu** ve **kullanıcı deneyimini** öncelikli olarak hedeflemiştir.

#### Test Odak Alanları

| Test Tipi | Amaç | Öncelik |
|-----------|------|---------|
| **Accuracy Testi** | ML modellerinin phishing/legitimate ayrımını doğru yapması | 🔴 Kritik |
| **Functional Testi** | Tüm UI bileşenlerinin ve API endpoint'lerinin çalışması | 🔴 Kritik |
| **Integration Testi** | Backend-Database-Cache entegrasyonu | 🟡 Yüksek |
| **Usability Testi** | Tema, dil, ayar kalıcılığı | 🟢 Orta |

#### Neden Accuracy Ölçüldü?

ML-based siber güvenlik sistemlerinde **False Positive** ve **False Negative** oranları kritik öneme sahiptir:
- **False Negative (kaçırılan phishing):** Güvenlik açığı, potansiyel data breach
- **False Positive (yanlış alarm):** Operasyonel verimlilik kaybı, user trust azalması

Bu nedenle accuracy, precision, recall ve F1-score metrikleri detaylı ölçülmüştür.

#### Neden Latency Detaylı Ölçülmedi?

1. **Kullanım Senaryosu:** CyberGuard, real-time stream processing değil, on-demand analiz sistemidir
2. **Acceptable Threshold:** 1-2 saniye response time, kullanıcı deneyimi için kabul edilebilir
3. **Baseline Karşılaştırma:** Mevcut performans (BERT: ~45ms, FastText: <1ms) kullanım senaryosu için yeterli

**Gelecek Çalışma:** Production deployment'ta P95/P99 latency ve throughput metrikleri Grafana ile monitör edilmelidir.

#### Neden Load Test Yapılmadı?

1. **Hedef Kitle:** Orta ölçekli kurumlar (10-100 concurrent user)
2. **Current Capacity:** Flask + Gunicorn (4 worker) bu senaryoyu karşılamaktadır
3. **Öncelik:** Fonksiyonel doğruluk > Yüksek concurrent load

**Gelecek Çalışma:** Kurumsal deployment öncesi Apache JMeter veya Locust ile load test yapılmalıdır.

### Fonksiyonel Test Sonuçları

| Test | Durum | Notlar |
|------|-------|--------|
| Dashboard yükleme | ✅ Pass | Tüm kartlar ve grafikler yükleniyor |
| Email phishing tespiti | ✅ Pass | 3 model doğru sonuç veriyor |
| Email legitimate tespiti | ✅ Pass | False positive düşük |
| Web anomali tespiti | ✅ Pass | SQL Injection, XSS tespit ediliyor |
| Web normal trafik | ✅ Pass | Normal trafik doğru sınıflandırılıyor |
| Korelasyon analizi | ✅ Pass | IP-based ve time-based korelasyon çalışıyor |
| Model karşılaştırma | ✅ Pass | Grafikler doğru render ediliyor |
| Demo data oluşturma | ✅ Pass | 30 email + 30 web + 5 koordineli saldırı |
| Tema değiştirme | ✅ Pass | Kalıcı olarak kaydediliyor |
| Dil değiştirme | ✅ Pass | TR/EN geçişi çalışıyor |
| Settings kaydetme | ✅ Pass | Tüm ayarlar persist ediliyor |
| Excel export | ✅ Pass | Dosya indiriliyor |

### Performans Metrikleri

| Metrik | Değer |
|--------|-------|
| API Yanıt Süresi (ortalama) | ~200ms |
| Email Analiz Süresi (TF-IDF) | ~25ms |
| Email Analiz Süresi (BERT) | ~45ms |
| Email Analiz Süresi (FastText) | <1ms |
| Web Log Analiz Süresi | ~15ms |
| Dashboard Yükleme | <1s |

---

## 📊 Model Karşılaştırması ve Trade-off Analizi

### Model Performans Karşılaştırması

| Model | Accuracy | Precision | Recall | F1-Score | Inference Time |
|-------|----------|-----------|--------|----------|----------------|
| **BERT (DistilBERT)** | %94-97 | %95 | %93 | %94 | ~45ms |
| **FastText** | %90-94 | %92 | %90 | %91 | <1ms |
| **TF-IDF + Random Forest** | %89.75 | %90 | %88 | %89 | ~25ms |

### Neden BERT Diğerlerinden Daha İyi Performans Gösterdi?

1. **Contextual Understanding:** BERT, kelimelerin bağlamını anlar. "Bank" kelimesi "river bank" ve "bank account" için farklı embedding üretir.

2. **Transfer Learning:** 1.5 milyar kelime üzerinde pre-train edilmiş model, phishing dataset'inde fine-tune edilmiştir. Genel dil anlayışı + domain-specific öğrenme.

3. **Subword Tokenization:** "PayPaI" (I harfi ile sahte PayPal) gibi typosquatting saldırılarını yakalayabilir.

4. **Attention Mechanism:** Hangi kelimelerin phishing tespitinde önemli olduğunu öğrenir ("urgent", "verify", "click").

### Hız vs Doğruluk Trade-off Analizi

```
                     HIZLI ◄─────────────────────────► YAVAŞ
                       │                                  │
                FastText                              BERT
                 (<1ms)                              (45ms)
                   │                                    │
                   ▼                                    ▼
              %90-94 Acc                          %94-97 Acc
                   │                                    │
                   │        ┌────────────┐              │
                   │        │  TF-IDF    │              │
                   │        │   (25ms)   │              │
                   │        │ %89.75 Acc │              │
                   │        └────────────┘              │
                   │                                    │
           ▲       ▼                                    ▼       ▲
         DÜŞÜK ACCURACY                          YÜKSEK ACCURACY
```

#### Kullanım Senaryosu Önerileri

| Senaryo | Önerilen Model | Gerekçe |
|---------|----------------|---------|
| **Real-time Email Gateway** | FastText | Yüksek throughput gerekli, <1ms latency |
| **Kritik Güvenlik Analizi** | BERT | Accuracy kritik, latency kabul edilebilir |
| **Balanced / Genel Kullanım** | TF-IDF + RF | İyi denge, açıklanabilirlik (LIME) |
| **Ensemble (Production)** | Üçü birlikte | En yüksek accuracy, weighted voting |

### False Positive / False Negative Analizi

#### False Positive Senaryoları (Meşru → Phishing olarak işaretlenen)

1. **Agresif Marketing E-postaları:** "Limited time offer!", "Act now!" gibi ifadeler
2. **IT Departmanı Uyarıları:** "Your password will expire" gibi legitimate sistem mesajları
3. **Kısa Mesajlar:** "Hey, how are you?" gibi çok kısa mesajlarda model güvensiz olabiliyordu *(Düzeltildi: v2.0'da short message detection eklendi)*

**Mitigation:** 
- Whitelist domain desteği eklenebilir
- Threshold ayarlanabilir (%50 → %60)
- Human-in-the-loop review süreci

#### False Negative Senaryoları (Phishing → Meşru olarak işaretlenen)

1. **Hedefli Spear Phishing:** Kişiselleştirilmiş, phishing keyword içermeyen saldırılar
2. **Zero-Day Phishing:** Yeni kampanyalar, training data'da olmayan pattern'ler
3. **Homograph Saldırıları:** "pаypal.com" (Kiril 'а' karakteri) gibi punycode saldırıları

**Mitigation:**
- VirusTotal API ile URL reputation check
- Domain age check (yeni kayıtlı domainler şüpheli)
- Sürekli model retraining (concept drift'e karşı)

### Concept Drift Riski

**Concept Drift:** Phishing saldırıları sürekli evrilir. 2025'te etkili olan phishing pattern'leri 2026'da değişmiş olabilir.

**Risk Faktörleri:**
- Yeni phishing kampanya temaları (AI-generated phishing, deepfake)
- Yeni sosyal mühendislik teknikleri
- Değişen e-posta formatları

**Önerilen Stratejiler:**
1. **Periyodik Retraining:** Her 3-6 ayda bir model güncellemesi
2. **Active Learning:** False positive/negative feedback'lerden öğrenme
3. **Ensemble Diversification:** Farklı feature'lara dayanan modeller kullanma
4. **Continuous Monitoring:** Accuracy metrikleri düşüşü için alerting

---

## 🚀 Kurulum ve Çalıştırma

### Hızlı Başlangıç (Docker)

```bash
# 1. Projeyi klonlayın
git clone https://github.com/username/UnifiedCyberThreatDetectionSystem.git
cd UnifiedCyberThreatDetectionSystem

# 2. Docker container'ları başlatın
docker-compose up -d

# 3. Servislere erişin
# Dashboard: http://localhost:5000
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

### Manuel Kurulum

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

## 📝 Sonuç

CyberGuard, modern yapay zeka teknolojilerini kullanarak kapsamlı bir siber güvenlik çözümü sunmaktadır:

- ✅ **3 farklı ML modeli** ile yüksek doğrulukta phishing tespiti
- ✅ **Modüler, servis-odaklı mimari** ile bakım kolaylığı
- ✅ **Bilinen tasarım kalıpları** (MVC, Event-Driven, Ensemble) ile sağlam altyapı
- ✅ **Gerçek zamanlı korelasyon analizi** ile koordineli saldırı tespiti
- ✅ **Trade-off bilinci** ile kullanım senaryosuna uygun model seçimi
- ✅ **Docker ile kolay dağıtım** ve production-ready altyapı

Sistem, özellikle orta ölçekli kurumlar için optimize edilmiş olup, gerektiğinde horizontal scaling ile genişletilebilir yapıdadır.

---

**© 2025-2026 CyberGuard Project Team**
