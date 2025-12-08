# 🎯 YAPILACAKLAR LİSTESİ - FİNAL HAZIRLIK

**Hocalardan Gelen İstekler + Kendi Fikirleriniz**  
**Başlangıç Tarihi**: 8 Aralık 2025  
**Hedef**: Final Sunumu Hazır Hale Getirmek

---

## 📋 KATEGORI 1: TEMEL ALTYAPI & UYGULAMALAR

### ✅ Yapılmış Olanlar:
- ✅ Database Layer (PostgreSQL + SQLAlchemy)
- ✅ REST API (FastAPI, 35 endpoint)
- ✅ Email Detection (TF-IDF + Random Forest)
- ✅ Web Log Analysis (Isolation Forest)
- ✅ Correlation Engine
- ✅ Basic Dashboard (Flask)
- ✅ Docker Setup (docker-compose.yml)
- ✅ Tests (38/38 passing)

### ❌ YAPILACAKLAR - ALTYAPI

#### **1. BACKEND-FRONTEND AYIRIMI**
- [ ] **1.1** Backend ve Frontend klasör yapısını kur
  - [ ] `backend/` klasörü oluştur (mevcut src/ buraya taşı)
  - [ ] `frontend/` klasörü oluştur (React/Vue için hazır yap)
  - [ ] `backend/requirements.txt` güncelle
  - [ ] `frontend/package.json` oluştur (React boilerplate)
  - [ ] Docker Compose'u yeni yapıya göre güncelle
  - **Sorumlu**: Temel kodu organize etmek
  - **Tahmini Süre**: 2-3 saat

#### **2. STATEFUL MODEL PERSISTENCE**
- [ ] **2.1** Model kaydetme sistemi
  - [ ] Email model pickle olarak kaydet (`models/email_model.pkl`)
  - [ ] Web analyzer model kaydet (`models/weblog_model.pkl`)
  - [ ] Model version tracking (hangi veri ile eğitildi)
  - [ ] Model load on startup (restart'ta yeniden eğitme)
  - [ ] Database'de model metadata saklama
  - **Dosya**: `src/database/models.py` güncelle + `src/models/persistence.py` oluştur
  - **Tahmini Süre**: 3-4 saat

#### **3. DOCKER OPTİMİZASYONU**
- [ ] **3.1** Multi-stage Docker build
  - [ ] Uvicorn container optimize et
  - [ ] Worker nodes için ayrı container (Celery)
  - [ ] Redis container (caching)
  - [ ] PostgreSQL persist volume
  - [ ] Environment file (.env.production)
  - **Dosya**: `docker-compose.yml` güncelle
  - **Tahmini Süre**: 3-4 saat

---

## 📋 KATEGORI 2: ML MODEL GELİŞTİRMESİ

### ❌ YAPILACAKLAR - ML MODELLER

#### **4. TF-IDF vs BERT KARŞILAŞTIRMASI**
- [ ] **4.1** BERT (DistilBERT) model eğit
  - [ ] DistilBERT pre-trained model indir
  - [ ] Emailler üzerinde fine-tuning yap
  - [ ] Inference script oluştur
  - **Dosya**: `src/email_detector/bert_detector.py` oluştur
  - **Tahmini Süre**: 6-8 saat

- [ ] **4.2** FastText model eğit
  - [ ] FastText embedding model eğit
  - [ ] Classifier üstüne koy (Random Forest)
  - **Dosya**: `src/email_detector/fasttext_detector.py` oluştur
  - **Tahmini Süre**: 4-5 saat

- [ ] **4.3** Karşılaştırma tablosu oluştur
  - [ ] Performance metrikleri (Accuracy, F1, Precision, Recall)
  - [ ] Inference zamanı (TF-IDF vs BERT vs FastText)
  - [ ] Model boyutu ve memory kullanımı
  - [ ] LIME explainability karşılaştırması
  - **Dosya**: `docs/MODEL_COMPARISON.md` oluştur
  - **Tahmini Süre**: 2-3 saat

#### **5. BERT vs YENİ MODELLERİN TESTI**
- [ ] **5.1** Benchmark testleri
  - [ ] Accuracy test (test set'te)
  - [ ] Speed test (inference time)
  - [ ] Memory profiling
  - **Dosya**: `tests/test_model_comparison.py` oluştur
  - **Tahmini Süre**: 3-4 saat

---

## 📋 KATEGORI 3: VERİ ENTEGRASYONU

### ❌ YAPILACAKLAR - VERİTABANI & VERİ

#### **6. KAGGLE VERİLERİ İNTEGRASYONU**
- [ ] **6.1** Kaggle verisi indirme
  - [ ] Phishing/spam email dataset bul (örn: "Phishing Dataset" Kaggle)
  - [ ] Web attack logs dataset bul
  - [ ] Malware URLs dataset bul
  - **Format**: CSV, JSON
  - **Tahmini Süre**: 1 saat (download + eksik data temizleme)

- [ ] **6.2** Veri import script geliştir
  - [ ] Kaggle CSV import script (`src/database/import_kaggle.py`)
  - [ ] Data validation ve cleaning
  - [ ] Duplicate detection ve removal
  - [ ] Batch import optimization (5000+ rows)
  - **Tahmini Süre**: 4-5 saat

- [ ] **6.3** Database schema'yı genişlet
  - [ ] Yeni columns ekle (severity, attack_type, vb)
  - [ ] Migration script oluştur
  - [ ] Existing veriyi yeni schema'ya aktar
  - **Dosya**: `src/database/migrations/` oluştur
  - **Tahmini Süre**: 3-4 saat

#### **7. DASHBOARD VERİ GIRIŞ TÜRLERI**
- [ ] **7.1** CSV upload özelliği
  - [ ] REST API endpoint: `POST /api/upload/csv`
  - [ ] Drag-drop file upload UI
  - [ ] Validation ve preview
  - **Tahmini Süre**: 3-4 saat

- [ ] **7.2** Manual data entry (form)
  - [ ] Single email analizi için form
  - [ ] Single web log analizi için form
  - [ ] Form validation frontend'de
  - **Tahmini Süre**: 2-3 saat

- [ ] **7.3** API integrasyonu
  - [ ] Real-time data feed (Webhook)
  - [ ] Batch processing endpoint
  - **Tahmini Süre**: 2-3 saat

---

## 📋 KATEGORI 4: SECURITY ENTEGRASYONLARI

### ❌ YAPILACAKLAR - SECURITY

#### **8. VIRUSTOTAL API ENTEGRASYONU**
- [ ] **8.1** VirusTotal API setup
  - [ ] API key alma (virustotal.com)
  - [ ] API wrapper sınıfı oluştur (`src/security/virustotal.py`)
  - [ ] Rate limiting impl (4 request/minute)
  - [ ] Error handling
  - **Tahmini Süre**: 2-3 saat

- [ ] **8.2** URL ve IP reputation check
  - [ ] Email'deki URL'leri extract et
  - [ ] VirusTotal'de check et
  - [ ] Sonuçları DB'ye kaydet
  - [ ] Risk score'a ekle
  - **Tahmini Süre**: 3-4 saat

- [ ] **8.3** VirusTotal endpoint'i
  - [ ] `GET /api/security/check-url` endpoint
  - [ ] `GET /api/security/check-ip` endpoint
  - [ ] Cache results (Redis)
  - **Tahmini Süre**: 2-3 saat

#### **9. ABUSE IPDB ENTEGRASYONU (OPTIONAL)**
- [ ] **9.1** AbuseIPDB API setup
  - [ ] API key alma
  - [ ] IP reputation check
  - [ ] Suspicious IP detection
  - **Tahmini Süre**: 2 saat (optional)

---

## 📋 KATEGORI 5: UI/UX GELİŞTİRMESİ

### ❌ YAPILACAKLAR - FRONTEND

#### **10. TÜRKÇE-İNGİLİZCE ARAYÜZ**
- [ ] **10.1** Dil seçim sistemi
  - [ ] Localization kütüphanesi (i18next veya benzeri)
  - [ ] Tüm UI metin'leri constant'a taşı
  - [ ] Language toggle button
  - [ ] LocalStorage'da dil seçimini kaydet
  - **Tahmini Süre**: 3-4 saat

- [ ] **10.2** Türkçe çeviriler
  - [ ] Dashboard'ın tamamı Türkçe'ye çevir
  - [ ] API error mesajları Türkçe
  - [ ] Tüm label'lar ve butonlar
  - **Tahmini Süre**: 2-3 saat

- [ ] **10.3** İngilizce çeviriler
  - [ ] Tüm UI İngilizcede hazır olsun
  - [ ] Professional terminology
  - **Tahmini Süre**: 1-2 saat

#### **11. GECE GÜNDÜZ MODU (DARK/LIGHT THEME)**
- [ ] **11.1** Theme system
  - [ ] CSS variables tanımla (colors, fonts)
  - [ ] Dark/Light palettes oluştur
  - [ ] Theme toggle button
  - [ ] LocalStorage'da tema kaydet
  - **Tahmini Süre**: 2-3 saat

- [ ] **11.2** Dark theme tasarla
  - [ ] Professional dark colors
  - [ ] Chart'lara uygun renk seçimi
  - [ ] Accessibility kontrol (contrast)
  - **Tahmini Süre**: 2-3 saat

#### **12. SİBER GÜVENLİK TEMALI TASARIM**
- [ ] **12.1** Risk level renklendirilmesi
  - [ ] Critical (Kırmızı)
  - [ ] High (Turuncu)
  - [ ] Medium (Sarı)
  - [ ] Low (Yeşil)
  - [ ] Info (Mavi)
  - **Tahmini Süre**: 1 saat

- [ ] **12.2** Security focused UI elements**
  - [ ] Threat level indicators
  - [ ] Real-time threat feed
  - [ ] Attack timeline visualization
  - [ ] Heat maps (IP addresses, domains)
  - **Tahmini Süre**: 4-5 saat

- [ ] **12.3** Charts ve Grafikleri güncelle
  - [ ] Real-time threat graph
  - [ ] Trend analysis (time-series)
  - [ ] Top threats table
  - [ ] Distribution charts
  - **Tahmini Süre**: 3-4 saat

#### **13. RESPONSIVE DESIGN**
- [ ] **13.1** Mobile-first approach
  - [ ] Dashboard mobil'de uyumlu
  - [ ] Touch-friendly buttons ve menus
  - [ ] Responsive grid layout
  - **Tahmini Süre**: 3-4 saat

---

## 📋 KATEGORI 6: DOCUMENTATION & ANALYSIS

### ❌ YAPILACAKLAR - DOKÜMANTASYON

#### **14. PROJE ANALİZİ MD DOSYASI**
- [ ] **14.1** Teknik analiz belgesini güncelle
  - [ ] Mevcut architecture'i dokument et
  - [ ] Risk scoring formula detayları
  - [ ] Model comparison results
  - [ ] Database schema diagram
  - [ ] API endpoint documentation
  - **Dosya**: `docs/PROJECT_ANALYSIS.md` güncelle/oluştur
  - **Tahmini Süre**: 3-4 saat

#### **15. README GÜNCELLEMESI**
- [ ] **15.1** Main README.md güncelle
  - [ ] Installation steps (updated)
  - [ ] Quick start guide
  - [ ] Architecture overview
  - [ ] Feature list
  - [ ] Performance benchmarks
  - [ ] Contributing guide
  - **Tahmini Süre**: 2-3 saat

- [ ] **15.2** Backend README
  - [ ] API documentation
  - [ ] Database setup
  - [ ] Model training
  - [ ] Configuration options
  - **Tahmini Süre**: 1-2 saat

- [ ] **15.3** Frontend README
  - [ ] Setup instructions
  - [ ] Development server
  - [ ] Build & deployment
  - [ ] Component structure
  - **Tahmini Süre**: 1-2 saat

#### **16. HOCALARDAN GELEN İSTEKLERİN CEVAPI**
- [ ] **16.1** Risk Scoring Formula Dokümantasyonu
  - [ ] Formül açıklama: (Email*0.4 + Web*0.4 + Correlation*0.2)
  - [ ] Neden bu ağırlıklara karar verdik
  - [ ] Alternative formüller araştırması
  - [ ] SIEM best practices
  - **Dosya**: `docs/RISK_SCORING.md` oluştur
  - **Tahmini Süre**: 2-3 saat

- [ ] **16.2** TF-IDF Seçim Nedeni
  - [ ] Neden TF-IDF seçildi (hız, LIME uyumluluğu)
  - [ ] BERT vs FastText vs TF-IDF karşılaştırması
  - [ ] Performance metrikleri tablosu
  - [ ] Sonuç ve öneriler
  - **Dosya**: `docs/MODEL_SELECTION.md` oluştur
  - **Tahmini Süre**: 2-3 saat

- [ ] **16.3** UI Türkçe/İngilizce Seçeneği
  - [ ] Türkçe-İngilizce switch implemented
  - [ ] Her sayfada dil seçeneği
  - [ ] Localization dosyaları
  - **Tahmini Süre**: 2-3 saat (16.10 ile birlikte)

- [ ] **16.4** Future Work Roadmap Implementation
  - [ ] Database kısmı (PostgreSQL ile yapılmış)
  - [ ] Docker container'lar
  - [ ] VirusTotal integration
  - [ ] Stateful models
  - [ ] Karşılaştırma tablosu
  - **Dosya**: `docs/ROADMAP.md` güncelle
  - **Tahmini Süre**: 1-2 saat

---

## 📋 KATEGORI 7: KOD ORGANİZASYONU

### ❌ YAPILACAKLAR - KOD STRÜKTÜRESİ

#### **17. PROJE YAPISI DÜZENLEME**
- [ ] **17.1** Backend klasör yapısı
  ```
  backend/
  ├── src/
  │   ├── api/
  │   ├── database/
  │   ├── email_detector/
  │   ├── web_analyzer/
  │   ├── security/         (NEW - VirusTotal)
  │   ├── models/           (NEW - Model persistence)
  │   └── unified_platform/
  ├── tests/
  ├── requirements.txt
  ├── .env.example
  └── docker/
  ```
  - **Tahmini Süre**: 2-3 saat

- [ ] **17.2** Frontend klasör yapısı
  ```
  frontend/
  ├── src/
  │   ├── components/
  │   ├── pages/
  │   ├── services/
  │   ├── i18n/            (Localization)
  │   ├── themes/          (Dark/Light)
  │   └── utils/
  ├── public/
  ├── package.json
  └── docker/
  ```
  - **Tahmini Süre**: 1-2 saat

---

## 📋 KATEGORI 8: MODELİ KULLANMA

### ❓ SORULARININ CEVABI

#### **18. DASHBOARD VERİ GIRIŞ - NASIL ÇALIŞTIRIYOR?**

**Mevcut Durum:**
- CSV'den veri import'u: `src/database/import_csv.py`
- REST API'dan email analiz: `POST /api/emails/analyze`
- Flask Dashboard: `web_dashboard/app.py`

**Nasıl Çalışıyor:**
1. **CSV Import** → `python src/database/import_csv.py`
2. **Manual Form** → Dashboard'dan email yaz, gönder
3. **API Çağrısı** → Analiz edil, DB'ye kaydet

**Yapılacak:**
- [ ] **18.1** CSV Upload özelliği (UI'dan)
  - Dashboard'a file upload button ekle
  - Backend'de `/api/upload/csv` endpoint
  - Real-time progress bar
  - **Tahmini Süre**: 3-4 saat

- [ ] **18.2** Batch email input
  - Paste multiple emails at once
  - Process them in parallel
  - **Tahmini Süre**: 2-3 saat

#### **19. NASIL ÇALIŞTIRILINIR - ESKİ vs YENİ**

**Eski Yöntem:**
```powershell
python main.py              # ML modelleri eğit
python run_dashboard.py     # Flask dashboard başlat
```

**YENİ YÖNTEM (FAZ 4-5 sonrası):**
```powershell
# Terminal 1: API başlat
python -m uvicorn src.api.main:app --reload

# Terminal 2: Dashboard başlat (Flask hala var)
python run_dashboard.py

# Terminal 3: Testleri çalıştır
python -m pytest -v
```

**FUTURE (Production):**
```powershell
docker-compose up -d
# Aynı anda:
# - API (port 8000)
# - Dashboard/Frontend (port 3000 - React)
# - PostgreSQL (port 5432)
# - Redis (port 6379)
```

**Yapılacak:**
- [ ] **19.1** Startup scripts
  - Windows: `start.bat` (tüm servisleri aç)
  - PowerShell: `start.ps1`
  - Linux: `start.sh`
  - **Tahmini Süre**: 1 saat

---

## 📋 KATEGORI 9: MODEL EĞİTİMİ

### ❓ MODEL EĞİTİMİ - NASIL?

**Mevcut Durum:**
- Email model: `src/email_detector/detector.py` → `train()` method
- Web model: `src/web_analyzer/analyzer.py` → `train()` method

**Nasıl Eğitiliyor:**
```python
# Email model eğit
from src.email_detector import EmailPhishingDetector
detector = EmailPhishingDetector()
detector.train('dataset/email_text.csv')  # TF-IDF + Random Forest

# Web model eğit
from src.web_analyzer import WebLogAnalyzer
analyzer = WebLogAnalyzer()
analyzer.train('dataset/web_logs.csv')    # Isolation Forest
```

**Yapılacak:**
- [ ] **19.1** Training script oluştur
  - `scripts/train_models.py` oluştur
  - Command line args (dataset path, model type, output path)
  - Progress bar
  - Validation metrics printing
  - **Tahmini Süre**: 2-3 saat

- [ ] **19.2** BERT model training
  - DistilBERT fine-tuning script
  - Hyperparameter tuning
  - Training & validation split
  - Model save
  - **Tahmini Süre**: 6-8 saat

- [ ] **19.3** FastText model training
  - FastText embedding generation
  - Classifier training
  - Model save
  - **Tahmini Süre**: 4-5 saat

- [ ] **19.4** Training dashboard
  - Real-time training progress
  - Metrics visualization
  - Model comparison live
  - **Tahmini Süre**: 3-4 saat

---

## 📋 KATEGORI 10: KAGGLE VERİ IMPORT

### ❓ DATABASE IMPORT - HANGİ DOSYA?

**Mevcut Import:**
```python
# src/database/import_csv.py
import_emails_from_csv('dataset')  # dataset/ klasöründe tüm CSV'leri import et
```

**Import Edilen Dosyalar:**
```
dataset/
├── email_text.csv
├── Enron.csv
├── human-legit.csv
├── human-phishing.csv
├── llm-legit.csv
├── llm-phishing.csv
├── Nigerian_Fraud.csv
├── phishing_email.csv
├── SpamAssasin.csv
└── ... (ve diğerleri)
```

**Yapılacak:**
- [ ] **20.1** Kaggle veri indirme
  - Phishing datasets bul
  - URL lists bul
  - Malware datasets bul
  - Download & local'e kaydet
  - **Tahmini Süre**: 1-2 saat

- [ ] **20.2** Kaggle importer script
  - `src/database/import_kaggle.py` oluştur
  - Kaggle API ile otomatik download
  - Data cleaning & validation
  - Batch insert optimization
  - **Tahmini Süre**: 3-4 saat

- [ ] **20.3** Data merge & deduplication
  - Existing + Kaggle verilerini birleştir
  - Duplicate detection
  - Inconsistent data cleaning
  - **Tahmini Süre**: 2-3 saat

---

## 📊 ÖZET TABLO - KAÇ SAATLİK İŞ VAR?

| Kategori | İş | Saat | Durum |
|----------|-----|------|-------|
| **Altyapı** | Backend-Frontend Ayırımı | 2-3 | ❌ |
| | Model Persistence | 3-4 | ❌ |
| | Docker Optimizasyonu | 3-4 | ❌ |
| **ML** | BERT Model | 6-8 | ❌ |
| | FastText Model | 4-5 | ❌ |
| | Model Karşılaştırması | 2-3 | ❌ |
| | Model Benchmark Testleri | 3-4 | ❌ |
| **Veri** | Kaggle Veri İndirme | 1-2 | ❌ |
| | Kaggle İmporter | 3-4 | ❌ |
| | Database Genişletme | 3-4 | ❌ |
| | Data Upload Özelliği | 3-4 | ❌ |
| **Security** | VirusTotal API | 2-3 | ❌ |
| | URL/IP Check | 3-4 | ❌ |
| | VirusTotal Endpoint | 2-3 | ❌ |
| | AbuseIPDB (optional) | 2 | ❌ |
| **Frontend** | Türkçe-İngilizce | 3-4 | ❌ |
| | Türkçe Çeviriler | 2-3 | ❌ |
| | Dark/Light Mode | 2-3 | ❌ |
| | Cybersecurity Tasarım | 4-5 | ❌ |
| | Charts & Graphs | 3-4 | ❌ |
| | Responsive Design | 3-4 | ❌ |
| **Dokümantasyon** | Proje Analizi | 3-4 | ❌ |
| | README Güncelleme | 4-5 | ❌ |
| | Risk Scoring Doc | 2-3 | ❌ |
| | Model Selection Doc | 2-3 | ❌ |
| | Roadmap Güncelleme | 1-2 | ❌ |
| **Kod Org.** | Backend Yapısı | 2-3 | ❌ |
| | Frontend Yapısı | 1-2 | ❌ |
| **Training** | Training Scripts | 2-3 | ❌ |
| | Training Dashboard | 3-4 | ❌ |
| | BERT Training | 6-8 | ❌ |
| **İsteğe Bağlı** | Startup Scripts | 1 | ❌ |
| | AbuseIPDB | 2 | ❌ |
| **TOPLAM** | | **≈120-150 saat** | |

---

## 🎯 ÖNEMLİ NOTLAR

### **HOCALARDAN ALINACAK YANIT:**
```
Arkadaşlar merhaba,
...
Özellikle Security & UI ve Database kısmını (Roadmap and Future Work)'te 
bahsettiğiniz yaparsanız güzel olur.
...
```

**Bu demek ki ÖNCE bunları yap:**
1. ✅ **Security & UI** (VirusTotal, Dark mode, Türkçe-İngilizce)
2. ✅ **Database** (Kaggle veri, schema genişletme)
3. ✅ **Model Karşılaştırması** (TF-IDF vs BERT)

### **PRESENTATION SIRALAMASI (FINAL İÇİN):**
1. **Risk Scoring Formula** - Neden bu formülü seçtik, SIEM best practices
2. **TF-IDF vs BERT Karşılaştırması** - Tablo, grafikler, sonuçlar
3. **Database + Kaggle Veri** - Schema, import process, statistics
4. **VirusTotal Integration** - URL/IP reputation, threat intel
5. **UI** - Dark/Light mode, Türkçe-İngilizce, cybersecurity design
6. **Future Work** - Neler yaptık, neler kaldı

---

## 📅 ÖNERILEN SIRA (YÜKSEKTİ DÜŞÜĞE)

**WEEK 1 (Şu hafta):**
1. Risk Scoring Doc'unu yazıver (2 saat) → Hocaya göster
2. Model Selection Doc'unu hazırla (2 saat)
3. BERT model eğitimini başlat (paralel olarak 6-8 saat)
4. Türkçe-İngilizce lokalizasyon (3-4 saat)

**WEEK 2:**
1. Dark/Light mode (2-3 saat)
2. Kaggle veri indirme ve import (3-4 saat)
3. Model Karşılaştırması tablosu (2-3 saat)

**WEEK 3:**
1. VirusTotal API integration (2-3 saat)
2. UI security tasarım (4-5 saat)
3. Backend-Frontend ayırımı (2-3 saat)

**WEEK 4:**
1. Final README & dokümantasyon (4-5 saat)
2. Testing & debugging (3-4 saat)
3. Demo hazırlama (2-3 saat)

---

## ✅ KONTROL LİSTESİ (FINAL İÇİN)

Sunumda bu dosyaları göster:
- [ ] Risk Scoring explanation document
- [ ] Model comparison table (TF-IDF vs BERT vs FastText)
- [ ] Database schema with Kaggle data
- [ ] VirusTotal integration example
- [ ] Dark/Light mode toggle working
- [ ] Turkish/English UI switch working
- [ ] Updated README with all features
- [ ] Architecture diagram with new components
- [ ] Test results showing improvements
- [ ] Performance benchmarks

---

**KALAN SORU: BAŞLANGIÇ YAPACAK MISIN?**

Hangi işe ilk başlasak? Seni ararım:
1. Risk Scoring döküman
2. BERT model eğitimi
3. Türkçe-İngilizce UI
4. Kaggle veri import
5. VirusTotal API

**Hangisini yapalım ilk?** 🚀
