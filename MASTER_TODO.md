# 📋 MASTER TODO LİSTESİ - MANTIKSAL SIRA

**Oluşturulma Tarihi**: 8 Aralık 2025  
**Durum**: ACTIVE  
**Toplam Görev**: 25 item  
**Tahmini Süre**: 50-60 saat

---

## 🎯 YAPILACAKLAR - MANTIKSAL SIRA

### **AŞAMA 1: TEMEL DOKÜMANTASYON (BITTI)** ✅

- [x] **1.1** Risk Scoring Detaylı Dokümantasyonu
  - [x] Formula açıklaması
  - [x] Ağırlık seçimi gerekçesi
  - [x] Alternatif formüller
  - [x] SIEM best practices
  - [x] Örnek hesaplamalar
  - ✅ **TAMAMLANDI**: `docs/RISK_SCORING_DETAILED.md`
  - ⏱️ **Harcanan Süre**: 2.5 saat
  - 📊 **Durum**: GIT'te kayıtlı

---

### **AŞAMA 2: MODEL EĞİTİMİ (BAŞLAYACAK)** 🔴

#### **2.1** BERT Model Eğitimi (PARALELde)
- [ ] **2.1.1** DistilBERT setup
  - [ ] Pre-trained model indir (400MB)
  - [ ] Environment kurulumu (transformers, torch)
  - [ ] Memory management (GPU/CPU)
  - **Dosya**: `src/email_detector/bert_detector.py`
  - **Tahmini Süre**: 1 saat (setup)
  - **Tahmini Eğitim Süresi**: 6-8 saat
  - **Başlangıç**: İKİ GÜN SONRA

- [ ] **2.1.2** Fine-tuning on email dataset
  - [ ] Training script yazma
  - [ ] Hyperparameter tuning
  - [ ] Validation metrics
  - [ ] Model save
  - **Tahmini Süre**: 2 saat (code)
  - **Tahmini Eğitim Süresi**: 6-8 saat
  - **Başlangıç**: İKİ GÜN SONRA

---

### **AŞAMA 3: MODEL KARŞILAŞTIRMASI (PARALEL)** 🟠

#### **3.1** FastText Model (Optional)
- [ ] **3.1.1** FastText embedding training
  - [ ] FastText model eğit
  - [ ] Word vectors oluştur
  - [ ] Classifier training
  - **Dosya**: `src/email_detector/fasttext_detector.py`
  - **Tahmini Süre**: 4-5 saat
  - **NOT**: BERT bitince yapabilirsin

#### **3.2** Model Karşılaştırması Tablosu
- [ ] **3.2.1** Benchmark metrikleri
  - [ ] Accuracy, F1-Score, Precision, Recall
  - [ ] Inference time karşılaştırması
  - [ ] Model size comparison
  - [ ] Memory usage
  - **Dosya**: `docs/MODEL_COMPARISON.md`
  - **Tahmini Süre**: 2-3 saat
  - **Başlangıç**: BERT eğitimi bittikten sonra

#### **3.3** Final Model Seçim
- [ ] **3.3.1** BERT vs TF-IDF vs FastText seçimi
  - [ ] Accuracy vs Speed trade-off
  - [ ] Production deployment seçimi
  - [ ] Confidence açıklaması
  - **Tahmini Süre**: 1 saat
  - **Başlangıç**: Karşılaştırma bittikten sonra

---

### **AŞAMA 4: VERITABANI & VERİ (PARALEL)** 🟠

#### **4.1** Kaggle Veri İntegrasyonu
- [ ] **4.1.1** Dataset bulma ve indir
  - [ ] Phishing/Spam email datasets bul
  - [ ] URL/Domain malware lists
  - [ ] Web attack logs
  - **Tahmini Süre**: 1-2 saat
  - **Başlangıç**: PARALEL - HEMEN BAŞLA

- [ ] **4.1.2** CSV Import Script
  - [ ] `src/database/import_kaggle.py` oluştur
  - [ ] Data cleaning & validation
  - [ ] Duplicate detection
  - [ ] Batch insert optimization
  - **Tahmini Süre**: 3-4 saat
  - **Başlangıç**: Datasets indirdikten sonra

- [ ] **4.1.3** Database Schema Genişletme
  - [ ] Email model'e severity ekle
  - [ ] WebLog model'e attack_type ekle
  - [ ] Migration script oluştur
  - [ ] Existing data migrate
  - **Tahmini Süre**: 2-3 saat
  - **Başlangıç**: Schema tasarımı bittikten sonra

#### **4.2** Data Quality Assurance
- [ ] **4.2.1** Verileri test et
  - [ ] 10000+ records import
  - [ ] Accuracy metrics kontrol
  - [ ] Data consistency check
  - **Tahmini Süre**: 1-2 saat
  - **Başlangıç**: Import bittikten sonra

---

### **AŞAMA 5: SECURITY ENTEGRASYONU** 🟠

#### **5.1** VirusTotal API
- [ ] **5.1.1** API Setup
  - [ ] Hesap oluştur (virustotal.com)
  - [ ] API key alma
  - [ ] Rate limiting (4 req/min)
  - **Tahmini Süre**: 1 saat
  - **Başlangıç**: PARALEL - HEMEN BAŞLA

- [ ] **5.1.2** Wrapper Sınıfı
  - [ ] `src/security/virustotal.py` oluştur
  - [ ] URL checking
  - [ ] IP reputation checking
  - [ ] Error handling
  - [ ] Caching (Redis)
  - **Tahmini Süre**: 2-3 saat
  - **Başlangıç**: API key aldıktan sonra

- [ ] **5.1.3** Email Integration
  - [ ] Email'deki URL'leri extract et
  - [ ] VirusTotal'de check et
  - [ ] Risk score'a ekle
  - **Tahmini Süre**: 2-3 saat
  - **Başlangıç**: Wrapper tamamlandıktan sonra

#### **5.2** API Endpoint'i
- [ ] **5.2.1** REST API Endpoint
  - [ ] `POST /api/security/check-url`
  - [ ] `GET /api/security/check-ip`
  - [ ] Response formatting
  - **Tahmini Süre**: 2 saat
  - **Başlangıç**: Integration bittikten sonra

#### **5.3** AbuseIPDB (Optional)
- [ ] **5.3.1** AbuseIPDB Integration
  - [ ] API setup
  - [ ] IP reputation check
  - **Tahmini Süre**: 1-2 saat
  - **NOT**: Opsiyonel, zamanı kalırsa

---

### **AŞAMA 6: FRONTEND & UI (PARALEL)** 🟠

#### **6.1** Türkçe-İngilizce Lokalizasyon
- [ ] **6.1.1** i18n Setup
  - [ ] i18next kütüphanesi ekle
  - [ ] Folder structure oluştur
  - [ ] Dashboard strings extract
  - **Dosya**: `frontend/src/i18n/`
  - **Tahmini Süre**: 1-2 saat
  - **Başlangıç**: PARALEL - HEMEN BAŞLA

- [ ] **6.1.2** Türkçe Çeviriler
  - [ ] Tüm UI metin'leri Türkçe'ye çevir
  - [ ] API error mesajları
  - [ ] Tüm label'lar ve butonlar
  - **Tahmini Süre**: 2-3 saat
  - **Başlangıç**: i18n setup bittikten sonra

- [ ] **6.1.3** İngilizce Çeviriler
  - [ ] Professional terminology
  - [ ] Native English checks
  - **Tahmini Süre**: 1-2 saat
  - **Başlangıç**: Türkçe bittikten sonra

#### **6.2** Dark/Light Mode
- [ ] **6.2.1** Theme System
  - [ ] CSS variables tanımla
  - [ ] Color palettes oluştur
  - [ ] Theme toggle button
  - [ ] LocalStorage persistence
  - **Tahmini Süre**: 2-3 saat
  - **Başlangıç**: PARALEL - HEMEN BAŞLA

- [ ] **6.2.2** Dark Theme Design
  - [ ] Professional dark colors
  - [ ] Chart colors (dark mode uyumlu)
  - [ ] Accessibility check (contrast)
  - **Tahmini Süre**: 2 saat
  - **Başlangıç**: Theme system bittikten sonra

#### **6.3** UI Geliştirmeler
- [ ] **6.3.1** Cybersecurity Themed Design
  - [ ] Risk level colors (Critical=Red, High=Orange, etc)
  - [ ] Threat level indicators
  - [ ] Real-time threat feed visualization
  - **Tahmini Süre**: 3-4 saat
  - **Başlangıç**: Dark/Light mode bittikten sonra

- [ ] **6.3.2** Time-Series Visualization
  - [ ] Real-time threat graph
  - [ ] Trend analysis charts
  - [ ] Attack timeline
  - **Tahmini Süre**: 3-4 saat
  - **Başlangıç**: Design bittikten sonra

---

### **AŞAMA 7: DOKÜMANTASYON GÜNCELLEME** 🟢

#### **7.1** README Güncelleme
- [ ] **7.1.1** Main README.md
  - [ ] Installation steps (updated)
  - [ ] Quick start guide
  - [ ] Feature list (new features)
  - [ ] Performance benchmarks
  - **Tahmini Süre**: 2 saat
  - **Başlangıç**: Tüm features bittikte sonra

- [ ] **7.1.2** Backend README
  - [ ] New models documentation
  - [ ] API endpoints update
  - [ ] Database schema
  - [ ] Configuration options
  - **Tahmini Süre**: 1-2 saat
  - **Başlangıç**: Backend completion

- [ ] **7.1.3** Frontend README
  - [ ] Localization guide
  - [ ] Theme setup
  - [ ] Component structure
  - [ ] Build instructions
  - **Tahmini Süre**: 1-2 saat
  - **Başlangıç**: Frontend completion

#### **7.2** Teknik Dokümantasyon
- [ ] **7.2.1** Architecture Update
  - [ ] Updated system diagram
  - [ ] Component interactions
  - [ ] Data flow (with new components)
  - **Tahmini Süre**: 1-2 saat
  - **Başlangıç**: All features complete

- [ ] **7.2.2** Deployment Guide Update
  - [ ] Docker updates
  - [ ] Environment variables (new)
  - [ ] Database migration steps
  - [ ] Production checklist
  - **Tahmini Süre**: 1-2 saat
  - **Başlangıç**: All features complete

---

### **AŞAMA 8: TESTING & VALIDATION** 🔴

#### **8.1** Model Testing
- [ ] **8.1.1** BERT Model Tests
  - [ ] Unit tests
  - [ ] Integration tests
  - [ ] Performance tests
  - **Tahmini Süre**: 2-3 saat
  - **Başlangıç**: BERT eğitimi bittikten sonra

- [ ] **8.1.2** Comparison Tests
  - [ ] Accuracy comparison
  - [ ] Speed comparison
  - [ ] Memory comparison
  - **Tahmini Süre**: 1-2 saat
  - **Başlangıç**: Karşılaştırma bittikten sonra

#### **8.2** API Testing
- [ ] **8.2.1** VirusTotal Endpoint Tests
  - [ ] URL checking test
  - [ ] IP checking test
  - [ ] Error handling test
  - **Tahmini Süre**: 1-2 saat
  - **Başlangıç**: API bittikten sonra

#### **8.3** Database Testing
- [ ] **8.3.1** Data Import Validation
  - [ ] 10000+ records test
  - [ ] Query performance
  - [ ] Data consistency
  - **Tahmini Süre**: 1-2 saat
  - **Başlangıç**: Import bittikten sonra

#### **8.4** UI Testing
- [ ] **8.4.1** Localization Testing
  - [ ] Türkçe/İngilizce switch test
  - [ ] All text rendering
  - [ ] Special characters
  - **Tahmini Süre**: 1 saat
  - **Başlangıç**: Localization complete

- [ ] **8.4.2** Theme Testing
  - [ ] Dark/Light mode toggle
  - [ ] All colors rendering
  - [ ] Contrast check
  - **Tahmini Süre**: 1 saat
  - **Başlangıç**: Dark/Light complete

#### **8.5** Integration Testing
- [ ] **8.5.1** End-to-End Test
  - [ ] Email upload → Analysis → Risk Score
  - [ ] Web log import → Analysis
  - [ ] Threat correlation
  - [ ] Report generation
  - **Tahmini Süre**: 2 saat
  - **Başlangıç**: All components complete

---

### **AŞAMA 9: FINAL SUNUMU HAZIRLAMA** 🟡

#### **9.1** Sunum Materyal Hazırlık
- [ ] **9.1.1** Slides Oluştur
  - [ ] Risk Scoring explanation
  - [ ] Model Comparison results
  - [ ] Database & Real data
  - [ ] Security features (VirusTotal)
  - [ ] UI improvements
  - [ ] Architecture diagrams
  - [ ] Future roadmap
  - **Tahmini Süre**: 3-4 saat
  - **Başlangıç**: Tüm work complete

#### **9.2** Demo Hazırlık
- [ ] **9.2.1** Live Demo Scripts
  - [ ] Email analysis demo
  - [ ] Risk scoring calculation
  - [ ] Dark/Light mode switch
  - [ ] Türkçe/İngilizce switch
  - [ ] VirusTotal API demo
  - [ ] Report generation
  - **Tahmini Süre**: 2 saat
  - **Başlangıç**: Tüm work complete

#### **9.3** Final Walkthrough
- [ ] **9.3.1** Sunum Rehearsal
  - [ ] Full demo run
  - [ ] Q&A hazırlığı
  - [ ] Timing check
  - **Tahmini Süre**: 2-3 saat
  - **Başlangıç**: Slides & Demo ready

---

## 📊 ÖZET TABLO

```
┌─────────────────────────────────────────────────────────────┐
│              YAPILACAKLAR ÖZET VE SIRA                       │
├─────────────────────────────────────────────────────────────┤
│ AŞAMA 1: Temel Dokümantasyon        ✅ TAMAMLANDI (2.5h)   │
│         Risk Scoring Doc                                     │
│                                                              │
│ AŞAMA 2: Model Eğitimi              🔴 SONRA (8h)          │
│         BERT + FastText                                      │
│                                                              │
│ AŞAMA 3: Model Karşılaştırması      🔴 SONRA (3h)          │
│         Benchmark + Selection                                │
│                                                              │
│ AŞAMA 4: Database & Veri (PARALEL)  🔴 SONRA (5-6h)        │
│         Kaggle + Import                                      │
│                                                              │
│ AŞAMA 5: Security (PARALEL)         🔴 SONRA (6-8h)        │
│         VirusTotal + Integration                             │
│                                                              │
│ AŞAMA 6: Frontend & UI (PARALEL)    🔴 SONRA (8-10h)       │
│         i18n + Dark/Light + Design                          │
│                                                              │
│ AŞAMA 7: Dokümantasyon              🟡 SON (6-8h)          │
│         README + Architecture                                │
│                                                              │
│ AŞAMA 8: Testing & Validation       🟡 SON (10-12h)        │
│         Comprehensive QA                                     │
│                                                              │
│ AŞAMA 9: Final Sunum                🟡 SON (7-9h)          │
│         Slides + Demo                                        │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│ TOPLAM TAHMINI SÜRE: 50-60 saat                             │
├─────────────────────────────────────────────────────────────┤
│ ✅ = Tamamlandı                                              │
│ 🔴 = Başlangıç işi (serial/parallel)                        │
│ 🟡 = Son işi (serial)                                       │
│ 🟠 = Paralel yapılabilecek                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗓️ HAFTALIK TAKVIM

```
📅 HAFTA 1 (ŞU HAFTA):
├─ Pazartesi-Salı:   Risk Scoring Doc ✅ BITTI
├─ Çarşamba:         BERT setup başlat (eğitim başlasın)
├─ Çarşamba-Perşembe: Kaggle veri bul & download (PARALEL)
└─ Perşembe-Cuma:    VirusTotal API setup (PARALEL)

📅 HAFTA 2:
├─ Pazartesi:        BERT eğitimi bitmesini bekle
├─ Pazartesi-Salı:   FastText model (PARALEL)
├─ Salı-Çarşamba:    Kaggle CSV import script
├─ Çarşamba-Perşembe: i18n setup + Türkçe çeviriler
└─ Perşembe-Cuma:    Dark/Light mode

📅 HAFTA 3:
├─ Pazartesi:        Model Karşılaştırması tablosu
├─ Salı:             VirusTotal integration to email
├─ Çarşamba:         Database schema update
├─ Perşembe:         UI Security design
└─ Cuma:             Integration testing

📅 HAFTA 4:
├─ Pazartesi-Salı:   Final documentation
├─ Çarşamba:         Final testing & bugfixes
├─ Perşembe:         Slides prepare
└─ Cuma:             Demo rehearsal
```

---

## ✅ BAŞLAMAK İÇİN AKSIYON

### **BUGÜN/YARININ BASINDAkİ ADIMLAR:**

1. **BERT Setup'ı İndir & Kur** (1 saat)
   ```powershell
   pip install transformers torch
   # BERT training script'i download
   ```

2. **Kaggle Datasets Bul** (1-2 saat)
   - Kaggle'da phishing datasets ara
   - Download başlat

3. **VirusTotal API Setup** (1 saat)
   - virustotal.com'a git
   - Account oluştur
   - API key al

4. **i18n Setup** (1-2 saat)
   - Frontend'e i18next ekle
   - Folder structure oluştur

### **PARALEL BAŞLAYACAKLAR:**
- BERT eğitimi (6-8 saat, tüm gece çalışabilir)
- Kaggle CSV import (3-4 saat code)
- VirusTotal API wrapper (2-3 saat)
- i18n + Dark/Light mode (3-4 saat)

---

## 🎯 İLK GÖREVLERİN SIRASI

1. ✅ **Risk Scoring Doc** (BITTI)
2. 🔴 **BERT Setup & Training Start** (HEMEN - PARALELde eğitsin)
3. 🟠 **Kaggle Datasets Download** (HEMEN PARALEL)
4. 🟠 **VirusTotal API Key** (HEMEN PARALEL)
5. 🟠 **i18n Frontend Setup** (HEMEN PARALEL)

**Bunları paralel yap, BERT eğitim süresi boyunca diğer işleri yap!**

---

**Son Güncelleme**: 8 Aralık 2025  
**Hazırlayan**: AI Assistant  
**Durum**: READY TO START 🚀
