# CyberGuard
## Birleşik Siber Tehdit Tespit Sistemi
### Proje Final Raporu

---

**Versiyon:** 2.0.0  
**Tarih:** Ocak 2026

---

## İÇİNDEKİLER

| Bölüm | Başlık | Sayfa |
|-------|--------|-------|
| 1 | Yönetici Özeti | 3 |
| 2 | Giriş ve Motivasyon | 4 |
| 3 | Sistem Genel Bakış | 5 |
| 4 | Yazılım Mimarisi ve Tasarım | 7 |
| 5 | Mimari Kalıplar ve Tasarım Desenleri | 11 |
| 6 | Sistem Özellikleri ve Kullanıcı Arayüzü | 14 |
| 7 | Yapay Zeka Modelleri | 18 |
| 8 | Test Metodolojisi ve Sonuçları | 22 |
| 9 | Model Karşılaştırması ve Trade-off Analizi | 25 |
| 10 | API Referansı | 29 |
| 11 | Kurulum ve Yapılandırma | 30 |
| 12 | Sonuç ve Gelecek Çalışmalar | 32 |

---

## 1. Yönetici Özeti

CyberGuard, kurumsal siber güvenlik ihtiyaçlarına yönelik geliştirilmiş, yapay zeka destekli bir tehdit tespit platformudur. Sistem, e-posta tabanlı phishing saldırıları ile web tabanlı saldırıları (SQL Injection, XSS, DDoS) gerçek zamanlı olarak tespit etme kapasitesine sahiptir.

Geleneksel güvenlik sistemleri imza tabanlı tespit yöntemlerine dayanmaktadır ve bu yaklaşım zero-day saldırıları ile sürekli evrilen tehditlere karşı yetersiz kalmaktadır. CyberGuard, yapay zeka teknolojilerini kullanarak bu sorunu çözmektedir.

### Temel Özellikler

| Özellik | Açıklama | Durum |
|---------|----------|-------|
| E-posta Phishing Tespiti | BERT, FastText ve TF-IDF modelleri ile ensemble analiz | ✅ Aktif |
| Web Log Analizi | Isolation Forest algoritması ile anomali tespiti | ✅ Aktif |
| Korelasyon Analizi | E-posta ve web tehditlerinin zaman/IP bazlı ilişkilendirilmesi | ✅ Aktif |
| Gerçek Zamanlı Dashboard | Chart.js ile interaktif grafikler ve anlık istatistikler | ✅ Aktif |
| Çoklu Dil Desteği | Türkçe ve İngilizce kullanıcı arayüzü | ✅ Aktif |
| Docker Deployment | 6 container ile production-ready dağıtım | ✅ Aktif |
| REST API | 15+ endpoint ile tam entegrasyon imkanı | ✅ Aktif |
| İzleme Altyapısı | Prometheus ve Grafana ile metrik toplama ve görselleştirme | ✅ Aktif |

---

## 2. Giriş ve Motivasyon

### Problemin Tanımı

Siber saldırılar her geçen gün daha sofistike hale gelmektedir. Özellikle phishing saldırıları, kurumlara yönelik en yaygın ve etkili tehdit vektörlerinden birini oluşturmaktadır. 2025 yılı itibarıyla, kurumsal veri ihlallerinin %90'ından fazlası phishing saldırılarıyla başlamaktadır.

Geleneksel güvenlik çözümleri şu kısıtlamalarla karşı karşıyadır:
- **İmza tabanlı tespit:** Yeni ve bilinmeyen tehditlerde yetersiz kalır
- **Yüksek false positive oranı:** Güvenlik ekiplerinin iş yükünü artırır
- **Tek vektör analizi:** Koordineli saldırıları tespit edemez
- **Açıklanamayan kararlar:** Neden bir şeyin tehdit olarak işaretlendiği anlaşılamaz

### Çözüm Yaklaşımı

CyberGuard, bu problemleri çözmek için yapay zeka tabanlı bir yaklaşım benimsemektedir:

1. **Örüntü öğrenimi:** Geçmiş verilerden öğrenerek yeni tehditleri tespit eder
2. **Çoklu model kullanımı:** Ensemble yaklaşım ile daha yüksek doğruluk ve düşük false positive
3. **Tehdit korelasyonu:** Farklı saldırı vektörlerini ilişkilendirir
4. **Açıklanabilir sonuçlar:** LIME ile model kararlarının gerekçesi görüntülenir

### Hedef Kitle

CyberGuard aşağıdaki kullanıcı grupları için tasarlanmıştır:
- Güvenlik Operasyon Merkezi (SOC) ekipleri
- IT güvenlik profesyonelleri
- Küçük ve orta ölçekli işletmeler
- Siber güvenlik alanında araştırma yapan akademisyenler ve öğrenciler

---

## 3. Sistem Genel Bakış

### 3.1 Amaç ve Hedefler

**Birincil Amaç:** Kurumsal ortamlarda e-posta ve web tabanlı siber tehditleri yapay zeka teknolojileri kullanarak otomatik olarak tespit etmek ve raporlamak.

**Hedefler:**
- Phishing e-postalarını %90 ve üzeri doğrulukla tespit etmek
- Web saldırı girişimlerini gerçek zamanlı olarak belirlemek
- Farklı vektörlerden gelen tehditleri ilişkilendirmek
- Güvenlik analistlerine kullanımı kolay bir arayüz sunmak
- Mevcut güvenlik altyapılarına API üzerinden entegre olmak

### 3.2 Kapsam

| Kapsam İçi | Kapsam Dışı |
|------------|-------------|
| E-posta phishing tespiti | Ağ trafiği analizi |
| Web log anomali analizi | Endpoint koruma |
| Tehdit korelasyonu | Malware analizi |
| Raporlama ve dışa aktarma | Otomatik müdahale |
| Çoklu dil desteği | Mobil uygulama |

### 3.3 Sistem Gereksinimleri

| Bileşen | Minimum | Önerilen |
|---------|---------|----------|
| İşletim Sistemi | Windows 10, Linux, macOS | Windows 11, Ubuntu 22.04 |
| Python | 3.8 | 3.10+ |
| RAM | 4GB | 8GB+ |
| Disk Alanı | 2GB | 5GB+ |
| Docker | 20.10+ | 24.0+ |
| Docker Compose | 1.29+ | 2.0+ |

### 3.4 Teknoloji Yığını

| Katman | Teknoloji | Versiyon | Kullanım Amacı |
|--------|-----------|----------|----------------|
| Backend | Python, Flask, Gunicorn | 3.8+, 2.0+, 21.0+ | REST API ve iş mantığı |
| Frontend | HTML5, CSS3, JavaScript | ES6+ | Kullanıcı arayüzü |
| Görselleştirme | Chart.js | 4.0+ | İnteraktif grafikler |
| Veritabanı | PostgreSQL | 15.0 | Kalıcı veri depolama |
| ORM | SQLAlchemy | 2.0+ | Veritabanı soyutlaması |
| Önbellek | Redis | 7.0+ | Performans iyileştirme |
| AI/ML | scikit-learn, PyTorch | 1.0+, 2.0+ | Makine öğrenimi |
| NLP | Transformers, NLTK, FastText | 4.0+, 3.8+ | Doğal dil işleme |
| Konteynerizasyon | Docker, Docker Compose | 24.0+, 2.0+ | Deployment |
| İzleme | Prometheus, Grafana | 2.45+, 10.0+ | Metrik ve monitoring |

---

## 4. Yazılım Mimarisi ve Tasarım

### 4.1 Mimari Karakterizasyon

CyberGuard, modüler ve servis-odaklı bir mimari üzerine inşa edilmiştir. Bu yaklaşım, sistemin farklı bileşenlerinin bağımsız olarak geliştirilmesine ve ölçeklenmesine olanak tanımaktadır.

Sistemin mimari karakteri şu şekilde özetlenebilir: Tehdit algılama mantığı ile sunum katmanları birbirinden ayrılmıştır ve bu ayrım, makine öğrenimi modellerinin bağımsız olarak geliştirilmesini mümkün kılmaktadır.

### 4.2 Mimari Paradigma

Sistem, temel olarak istek-yanıt (request-response) paradigmasını kullanmaktadır. Ancak tehdit tespiti ve korelasyon analizi bileşenlerinde olay-güdümlü (event-driven) yaklaşım benimsenmiştir. Bu hibrit mimari, hem kullanıcı etkileşimlerinin senkron işlenmesini hem de tehdit verilerinin asenkron olarak işlenmesini sağlamaktadır.

| Bileşen | Paradigma | Açıklama |
|---------|-----------|----------|
| Dashboard → API | Request-Response | Kullanıcı istekleri senkron olarak işlenir |
| Email/Web Log → Detection | Event-Driven | Gelen veriler event olarak işlenir |
| Detection → Correlation | Publisher-Subscriber | Tehditler korelasyon motoruna publish edilir |
| Correlation → Alerts | Event-Driven | Koordineli saldırılarda alert event'leri oluşur |

### 4.3 Katmanlı Mimari

Sistem, dört ana katmandan oluşmaktadır:

| Katman | Teknoloji | Sorumluluk |
|--------|-----------|------------|
| Sunum Katmanı (View) | Flask Dashboard + Jinja2 + JavaScript | Kullanıcı etkileşimi, form işleme, veri görselleştirme |
| Uygulama Katmanı (Controller) | Flask REST API Routes | İş mantığı orkestrasyon, girdi doğrulama, yanıt formatlama |
| İş Mantığı Katmanı (Model) | Email Detector, Web Analyzer, Correlation Engine | ML inference, özellik çıkarımı, risk skorlama |
| Veri Katmanı (Persistence) | PostgreSQL + Redis + File System | Veri kalıcılığı, önbellekleme, model depolama |

### 4.4 Mimari Diyagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         KULLANICI ARAYÜZÜ KATMANI                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │
│  │  Dashboard  │ │   Email     │ │   Web Log   │ │    Raporlar     │   │
│  │   Paneli    │ │   Analizi   │ │   Analizi   │ │   & Ayarlar     │   │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └────────┬────────┘   │
└─────────┼───────────────┼───────────────┼─────────────────┼────────────┘
          │               │               │                 │
          └───────────────┼───────────────┼─────────────────┘
                          ▼               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          FLASK REST API KATMANI                          │
│  /api/email/*  │  /api/predict/*  │  /api/correlation/*  │  /api/*     │
└─────────────────────────────────────────────────────────────────────────┘
                          │               │
          ┌───────────────┼───────────────┼───────────────┐
          ▼               ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│    BERT     │  │  FastText   │  │  TF-IDF+RF  │  │  Isolation  │
│ (DistilBERT)│  │   Model     │  │   Model     │  │   Forest    │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
                          │               │
                          ▼               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          VERİ KATMANI                                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │ PostgreSQL │  │   Redis    │  │ Prometheus │  │  Grafana   │        │
│  │ (Veritabanı)│ │  (Cache)   │  │ (Metrikler)│  │ (Dashboard)│        │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘        │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.5 Tasarım Kararları ve Gerekçeleri

#### E-posta ve Web Log Analizinin Aynı Backend'de Birleştirilmesi

Sistemde e-posta phishing tespiti ve web log analizi tek bir Flask API backend'inde birleştirilmiştir. Bu tasarım kararının arkasında birkaç önemli gerekçe bulunmaktadır:

**Korelasyon Avantajı:** Aynı IP adresinden gelen phishing e-postası ve web saldırısı, paylaşımlı veri katmanı sayesinde hızlıca ilişkilendirilebilir. Ayrı sistemlerde bu korelasyon, ek veri aktarımı ve senkronizasyon gerektirecekti.

**Kaynak Verimliliği:** Tek container kullanımı, düşük bellek ayak izi sağlar ve küçük ile orta ölçekli kurumlar için ideal bir çözüm sunar.

**Deployment Basitliği:** Tek docker image ile kolay bakım ve güncelleme mümkün olmaktadır.

**Veri Tutarlılığı:** Merkezi PostgreSQL veritabanı, tüm tehdit verileri için tek gerçeklik kaynağı (single source of truth) olarak işlev görmektedir.

Alternatif olarak mikroservis mimarisine geçiş düşünülmüştür; ancak mevcut kullanım senaryosu için bu yaklaşım aşırı mühendislik (overengineering) olarak değerlendirilmiştir. Yüksek ölçeklenebilirlik ihtiyacı doğduğunda bu geçiş gerçekleştirilebilir.

#### Model Inference'ın API İçinde Çalıştırılması

ML modelleri (BERT, FastText, TF-IDF) doğrudan Flask API container'ı içinde çalıştırılmaktadır. Bu kararın gerekçeleri şunlardır:

**Gecikme Optimizasyonu:** Model ile API arasındaki ağ atlaması elimine edilmiştir. Bu sayede yaklaşık 5-10ms tasarruf sağlanmaktadır.

**Oturum Durumu:** Modeller uygulama başlatıldığında bir kez yüklenir ve bellekte tutulur. Cold start problemi yaşanmaz.

**Hata Ayıklama Kolaylığı:** Uçtan uca izleme tek process içinde yapılabilir.

**Kaynak İzolasyonu:** Docker container zaten izolasyon sağlamaktadır.

Bu yaklaşımın yatay ölçeklemeyi zorlaştırdığı bilinmektedir. Yüksek throughput senaryolarında TensorFlow Serving veya TorchServe gibi ayrılmış inference sunucularına geçiş önerilmektedir.

### 4.6 Veri Akışı

Sistemdeki veri akışı şu adımları takip etmektedir:

1. **Kullanıcı Girdisi:** Kullanıcı, dashboard üzerinden e-posta içeriği veya web log verisi gönderir
2. **API İşleme:** Flask API isteği alır ve doğrular
3. **Model Çıkarımı:** Uygun ML modeli/modelleri girdiyi analiz eder
4. **Sonuç Depolama:** Tahminler PostgreSQL veritabanına kaydedilir
5. **Yanıt:** Sonuçlar güven skorları ile birlikte kullanıcıya döndürülür
6. **Korelasyon:** Arka plan işlemi ilgili tehditleri ilişkilendirir
7. **İzleme:** Prometheus metrikleri toplar, Grafana dashboard'ları görüntüler

---

## 5. Mimari Kalıplar ve Tasarım Desenleri

### 5.1 Genel Yaklaşım

CyberGuard sistemi, yazılım mühendisliğinde bilinen birçok mimari ve tasarım kalıbını uygulamaktadır. Sistem başlangıçta tek bir model etrafında tasarlanmamış olsa da, modüler yapısı doğal olarak Model-View-Controller (MVC) ve olay-güdümlü prensiplerle uyumludur. Bu yaklaşım, sistemin bakım kolaylığını, ölçeklenebilirliğini ve genişletilebilirliğini artırmaktadır.

### 5.2 Pattern-Mapping Tablosu

Aşağıdaki tablo, kullanılan mimari kalıpları ve bunların sistemdeki somut uygulamalarını göstermektedir:

| Mimari Kalıp / Tasarım Deseni | CyberGuard'daki Uygulama |
|-------------------------------|--------------------------|
| Model-View-Controller (MVC) | Dashboard HTML/JS (View), Flask API Routes (Controller), PostgreSQL + ML Models (Model) |
| Event-Driven / Publisher-Subscriber | Email/Web log alımı → Tespit → Korelasyon → Alert zinciri |
| Ensemble Learning Pattern | BERT, FastText ve TF-IDF sonuçlarının ağırlıklı oylama ile birleştirilmesi (ağırlıklar: 0.5, 0.3, 0.2) |
| Cache-Aside Pattern | Redis ile sık erişilen dashboard istatistiklerinin önbelleklenmesi (TTL: 60 saniye) |
| Repository Pattern | SQLAlchemy ORM ile veritabanı soyutlaması |
| Factory Pattern | get_bert_detector(), get_fasttext_detector() singleton-benzeri instance yönetimi |
| Strategy Pattern | Tüm dedektörler predict() ve predict_with_explanation() arayüzünü uygular |
| Façade Pattern | /api/email/analyze/hybrid endpoint'i üç modeli tek arayüz arkasında birleştirir |
| Circuit Breaker Pattern | VirusTotal API erişilemez olduğunda ML tabanlı tespit ile devam edilir |

### 5.3 Kalıp Seçim Gerekçeleri

#### Model-View-Controller (MVC) Kullanımı

MVC kalıbının tercih edilmesinin üç temel nedeni bulunmaktadır:

**Sorumluluk Ayrımı:** Frontend geliştiricisi, API detaylarını bilmeden kullanıcı arayüzünü değiştirebilir. Backend geliştiricisi ise sunum katmanından bağımsız olarak iş mantığını geliştirebilir.

**Test Edilebilirlik:** Controller mantığı, View'dan bağımsız olarak birim testlere tabi tutulabilir.

**Yeniden Kullanılabilirlik:** Aynı API, farklı frontend'lerden (web, mobil, CLI) kullanılabilir.

#### Ensemble Learning Kullanımı

Birden fazla modelin birlikte kullanılması şu avantajları sağlamaktadır:

**Tek Hata Noktası Eliminasyonu:** Bir model başarısız olsa bile diğerleri çalışmaya devam eder.

**Doğruluk Artışı:** Ensemble yaklaşım, genellikle tek modelden daha iyi performans gösterir.

**Açıklanabilirlik:** Her modelin nasıl karar verdiği ayrı ayrı görüntülenebilir ve karşılaştırılabilir.

#### Cache-Aside Kullanımı

Redis önbellek kullanımının gerekçeleri:

**Dashboard Yükleme Hızı:** Yaklaşık 1 saniyeden 200 milisaniyeye düşürülmüştür.

**Veritabanı Yükü Azaltımı:** Sık tekrarlanan sorgular önbellekten karşılanır.

**Basitlik:** Daha karmaşık write-through pattern'lere gerek kalmamıştır.

---

## 6. Sistem Özellikleri ve Kullanıcı Arayüzü

### 6.1 Ana Panel (Dashboard)

Dashboard, sistemin merkezi kontrol paneli olarak işlev görmektedir. Aşağıdaki bileşenlerden oluşmaktadır:

| Bileşen | Konum | İşlev |
|---------|-------|-------|
| E-posta Analizi Kartı | Sol üst | Toplam analiz edilen e-posta sayısı ve phishing oranı |
| Web Anomali Kartı | Orta üst | Web log analiz sayısı ve anomali oranı |
| Toplam Tehdit Kartı | Sağ üst | Tüm vektörlerden tespit edilen tehdit sayısı |
| Sistem Durumu Kartı | Sağ üst | API ve model yükleme durumu (yüzde olarak) |
| Tehdit Dağılımı Grafiği | Sol alt | Donut chart: Phishing vs Legitimate dağılımı |
| Model Performans Grafiği | Sağ alt | Bar chart: Model bazlı doğruluk oranları |
| Son Uyarılar | Alt | En son tespit edilen tehditler ve önem dereceleri |

**Üst Menü Butonları:**
- **Generate Demo Data:** Test amaçlı örnek veri seti oluşturur (30 e-posta + 30 web log + 5 koordineli saldırı)
- **Clear History:** Tüm geçmiş verileri siler ve istatistikleri sıfırlar
- **Tema Değiştir:** Aydınlık/Karanlık mod arasında geçiş yapar
- **Dil Değiştir:** Arayüz dilini Türkçe veya İngilizce olarak değiştirir

### 6.2 E-posta Analizi

E-posta analizi sayfası, kullanıcıların e-posta içeriklerini analiz etmesine olanak tanır.

**Giriş Alanları:**
- **Email Subject (Konu):** E-postanın konu satırı
- **From Address (Gönderen):** Gönderen e-posta adresi
- **Email Body (İçerik):** E-postanın tam metin içeriği

**Analiz Sonuç Bölümü:**
Her üç model için ayrı ayrı sonuçlar gösterilir:
- **BERT Panel:** En yüksek doğruluklu model, bağlamsal anlam çıkarımı yapar
- **FastText Panel:** En hızlı model, yüksek hacimli işlemler için idealdir
- **TF-IDF Panel:** Geleneksel model, açıklanabilir sonuçlar sunar (LIME)

**Sonuç Gösterimi:**
Her model için tahmin (PHISHING/LEGITIMATE), güven skoru (0-100%), risk seviyesi (Critical/High/Medium/Low) ve öne çıkan özellikler gösterilir.

**Örnek Tespit:**
- Girdi: "URGENT: Your account will be suspended! Click here immediately..."
- Sonuç: PHISHING tespit edildi, %95+ güven ile tüm modellerde

### 6.3 Web Log Analizi

Web log analizi sayfası, sunucu loglarını analiz ederek saldırı girişimlerini tespit eder.

**Giriş Alanları:**
- **IP Address:** İstemci IP adresi (bilinen kötü niyetli IP'ler işaretlenir)
- **HTTP Method:** GET, POST, PUT, DELETE vb.
- **Request Path:** İstenen URL yolu (SQL injection kalıpları aranır)
- **Status Code:** HTTP yanıt kodu (çok sayıda 401/403 şüphelidir)
- **User Agent:** Tarayıcı/bot bilgisi (sqlmap, nikto vb. tespit edilir)
- **Response Size:** Yanıt boyutu (anormal boyutlar veri sızıntısına işaret edebilir)

**Tespit Edilen Saldırı Türleri:**
- SQL Injection
- Cross-Site Scripting (XSS)
- Path Traversal
- Brute Force
- Bot/Crawler Activity
- DDoS Patterns

### 6.4 Korelasyon Analizi

Korelasyon analizi, e-posta ve web tehditlerini zaman ve IP bazında ilişkilendirir.

**Korelasyon Metrikleri:**
- **Korelasyon Skoru:** Pearson korelasyon katsayısı (-1 ile +1 arası)
- **Korelasyon Gücü:** Very Weak / Weak / Moderate / Strong sınıflandırması
- **Koordineli Saldırı Sayısı:** Aynı saat diliminde hem e-posta hem web tehdidi tespit edilen durumlar
- **IP Boost:** Aynı IP'den hem phishing hem web saldırısı geldiğinde eklenen bonus skor

**Grafikler:**
- **Threat Timeline Correlation:** Saat bazında e-posta ve web tehditlerinin çakışma grafiği
- **Email vs Web Comparison:** İki vektörün karşılaştırmalı bar chart'ı
- **Correlation Heatmap:** Tehdit korelasyonunun ısı haritası görselleştirmesi

### 6.5 Model Karşılaştırma

Model karşılaştırma sayfası, tüm yapay zeka modellerinin performans metriklerini yan yana görüntüler.

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| BERT (DistilBERT) | %94-97 | %95 | %93 | %94 |
| FastText | %90-94 | %92 | %90 | %91 |
| TF-IDF + Random Forest | %89.75 | %90 | %88 | %89 |
| Isolation Forest (Web) | %92+ | N/A | N/A | N/A |

### 6.6 Raporlar ve Ayarlar

**Raporlar - Dışa Aktarma:**
- **Export to Excel:** Tüm tehdit verilerini .xlsx formatında indirir
- **Export to JSON:** API entegrasyonu için JSON formatında dışa aktarır

**Raporlar - İçe Aktarma:**
- **Import from Excel:** Toplu e-posta veya web log verisi yüklemek için
- **Import from JSON:** Programatik veri aktarımı için

**Ayar Seçenekleri:**

| Ayar | Tür | Açıklama |
|------|-----|----------|
| Dark Mode | Toggle | Karanlık/Aydınlık tema tercihi |
| Language | Seçim | Arayüz dili: İngilizce veya Türkçe |
| Detection Threshold | Slider | Phishing tespit eşiği (0.0 - 1.0) |
| High Risk Alerts | Toggle | Yüksek riskli tehditler için bildirim |

**Ayar Kalıcılığı:** Tüm ayarlar hem localStorage (anlık tepki için) hem de PostgreSQL veritabanına (kalıcı depolama için) kaydedilir.

---

## 7. Yapay Zeka Modelleri

### 7.1 BERT (DistilBERT)

BERT (Bidirectional Encoder Representations from Transformers), sistemdeki en doğru modeldir.

| Özellik | Değer |
|---------|-------|
| Mimari | DistilBERT (BERT'in damıtılmış versiyonu) |
| Parametre Sayısı | 66 milyon |
| Kaynak | Hugging Face Transformers kütüphanesi |
| Eğitim Verisi | 31,000+ e-posta (CEAS, Enron, Nigerian Fraud, SpamAssassin) |
| Fine-tuning | Önceden eğitilmiş DistilBERT üzerinden transfer öğrenme |
| Tokenizer | WordPiece, 30,522 kelime dağarcığı |
| Doğruluk | %94-97 |
| İşlem Süresi | ~45ms / e-posta |

**Avantajları:**
- Bağlamı anlar: "Click here to verify" şüpheli iken "Click here to view the report" olmayabilir
- Yazım hatalarını ve varyasyonları yakalar: "Paypa1" vs "PayPal"
- Semantik anlam çıkarımı: Aciliyet, tehdit, ödül gibi kavramları öğrenir

**Dezavantajı:**
- Diğer modellere göre daha yavaş işlem süresi

### 7.2 FastText

FastText, Facebook Research tarafından geliştirilen hızlı metin sınıflandırma modeli.

| Özellik | Değer |
|---------|-------|
| Mimari | Word embedding + Linear classifier |
| Kaynak | Facebook Research |
| Model Boyutu | 881 MB |
| Doğruluk | %90-94 |
| İşlem Süresi | <1ms / e-posta |

**Avantajları:**
- Çok hızlı işlem süresi
- Yüksek hacimli real-time işlemler için ideal
- Alt-kelime (subword) bilgisini kullanır

**Dezavantajı:**
- Karmaşık bağlam anlamada BERT'e göre zayıf

### 7.3 TF-IDF + Random Forest

Geleneksel makine öğrenimi yaklaşımı kullanan model.

| Özellik | Değer |
|---------|-------|
| Mimari | TF-IDF vektörizasyon + Random Forest ensemble |
| Eğitim | SMOTE ile dengelenmiş veri seti |
| Doğruluk | %89.75 |
| ROC-AUC | %97.50 |
| İşlem Süresi | ~25ms / e-posta |
| Model Boyutu | ~50 MB |

**Avantajları:**
- Açıklanabilir sonuçlar (LIME ile özellik önem sıralaması)
- Hafif model boyutu
- Eğitimi kolay

**Dezavantajı:**
- Deep learning modellere göre düşük doğruluk

### 7.4 Isolation Forest (Web Analizi)

Denetimsiz anomali tespiti için kullanılan model.

| Özellik | Değer |
|---------|-------|
| Mimari | Unsupervised anomaly detection |
| Kullanım Alanı | Web log anomali tespiti |
| Doğruluk | %92+ |
| İşlem Süresi | ~15ms / log |
| Tespit Edilen Saldırılar | SQL Injection, XSS, DDoS, Brute Force |

### 7.5 Ensemble Yaklaşımı

Sistemde üç e-posta modeli, ağırlıklı oylama (weighted voting) ile birleştirilmektedir:

| Model | Ağırlık | Gerekçe |
|-------|---------|---------|
| BERT | 0.5 | En yüksek doğruluk |
| FastText | 0.3 | Hız ve çeşitlilik |
| TF-IDF | 0.2 | Açıklanabilirlik |

Bu ensemble yaklaşımı, tek modele göre daha yüksek doğruluk ve düşük false positive oranı sağlamaktadır.

---

## 8. Test Metodolojisi ve Sonuçları

### 8.1 Test Stratejisi

CyberGuard için tasarlanan test stratejisi, sistemin temel güvenlik fonksiyonlarının doğruluğunu ve kullanıcı deneyimini öncelikli hedef olarak belirlemiştir. Siber güvenlik sistemlerinde, yanlış tespit oranlarının kritik sonuçları olabileceğinden, doğruluk (accuracy) testleri ön plana çıkmaktadır.

### 8.2 Test Odak Alanları

| Test Tipi | Amaç | Öncelik |
|-----------|------|---------|
| Doğruluk Testi | ML modellerinin phishing/legitimate ayrımını doğru yapması | Kritik |
| Fonksiyonel Test | Tüm UI bileşenlerinin ve API endpoint'lerinin çalışması | Kritik |
| Entegrasyon Testi | Backend-Database-Cache entegrasyonu | Yüksek |
| Kullanılabilirlik Testi | Tema, dil, ayar kalıcılığı | Orta |

### 8.3 Test Yaklaşımı Açıklamaları

#### Doğruluk (Accuracy) Testlerinin Önemi

Makine öğrenimi tabanlı siber güvenlik sistemlerinde False Positive ve False Negative oranları kritik öneme sahiptir:

**False Negative (kaçırılan phishing):** Gerçek bir phishing e-postası "legitimate" olarak sınıflandırılırsa, kullanıcı saldırıya maruz kalabilir, veri ihlali yaşanabilir ve kurumsal güvenlik tehlikeye girebilir.

**False Positive (yanlış alarm):** Meşru bir e-posta "phishing" olarak işaretlenirse, operasyonel verimlilik düşer, kullanıcı güveni azalır ve güvenlik ekiplerinin iş yükü artar.

Bu nedenle accuracy, precision, recall ve F1-score metrikleri detaylı olarak ölçülmüş ve raporlanmıştır.

#### Gecikme (Latency) Testleri Hakkında

Detaylı gecikme testleri şu nedenlerle kapsamlı olarak gerçekleştirilmemiştir:

**Kullanım Senaryosu:** CyberGuard, gerçek zamanlı akış işleme (real-time stream processing) yerine talep üzerine analiz (on-demand analysis) sistemi olarak tasarlanmıştır. Kullanıcı bir e-posta veya log kaydı gönderir ve sonucu bekler.

**Kabul Edilebilir Eşik:** 1-2 saniye yanıt süresi, kullanıcı deneyimi açısından kabul edilebilir düzeydedir. Mevcut sistemde ortalama yanıt süresi 200ms civarındadır.

**Gelecek Çalışma:** Production ortamına geçişte P95/P99 gecikme metrikleri Grafana ile sürekli izlenmelidir.

#### Yük (Load) Testleri Hakkında

Kapsamlı yük testleri şu nedenlerle kapsam dışı bırakılmıştır:

**Hedef Kitle:** Sistem, orta ölçekli kurumlar (10-100 eşzamanlı kullanıcı) için optimize edilmiştir.

**Mevcut Kapasite:** Flask + Gunicorn (4 worker) yapılandırması bu senaryoyu karşılamaktadır.

**Gelecek Çalışma:** Kurumsal düzeyde deployment öncesinde Apache JMeter veya Locust ile yük testleri yapılmalıdır.

### 8.4 Fonksiyonel Test Sonuçları

| Test | Sonuç |
|------|-------|
| Dashboard yükleme ve grafikler | ✅ Başarılı |
| E-posta phishing tespiti (3 model) | ✅ Başarılı |
| E-posta legitimate sınıflandırma | ✅ Başarılı |
| Web log anomali tespiti | ✅ Başarılı |
| Web log normal trafik sınıflandırma | ✅ Başarılı |
| Korelasyon analizi hesaplama | ✅ Başarılı |
| Koordineli saldırı tespiti | ✅ Başarılı |
| Tema değiştirme ve kalıcılık | ✅ Başarılı |
| Dil değiştirme (TR/EN) | ✅ Başarılı |
| Ayar kaydetme ve yükleme | ✅ Başarılı |
| Excel dışa aktarma | ✅ Başarılı |
| JSON dışa aktarma | ✅ Başarılı |

### 8.5 Performans Metrikleri

| Metrik | Ölçüm |
|--------|-------|
| API ortalama yanıt süresi | ~200ms |
| BERT analiz süresi | ~45ms |
| FastText analiz süresi | <1ms |
| TF-IDF analiz süresi | ~25ms |
| Isolation Forest analiz süresi | ~15ms |
| Dashboard tam yükleme | <1 saniye |
| Demo data oluşturma (60 kayıt) | ~2 saniye |

---

## 9. Model Karşılaştırması ve Trade-off Analizi

### 9.1 Performans Karşılaştırması

| Model | Accuracy | Precision | Recall | F1-Score | Inference Time |
|-------|----------|-----------|--------|----------|----------------|
| BERT (DistilBERT) | %94-97 | %95 | %93 | %94 | ~45ms |
| FastText | %90-94 | %92 | %90 | %91 | <1ms |
| TF-IDF + Random Forest | %89.75 | %90 | %88 | %89 | ~25ms |

### 9.2 BERT'in Üstün Performansı

BERT modeli diğerlerine göre daha yüksek doğruluk göstermektedir. Bu durumun teknik nedenleri şunlardır:

**Bağlamsal Anlama:** BERT, kelimelerin bağlamını anlamaktadır. Örneğin, "bank" kelimesi "river bank" ve "bank account" ifadelerinde farklı embedding'ler üretir.

**Transfer Öğrenme:** Model, 1.5 milyar kelime üzerinde önceden eğitilmiştir. Bu geniş bilgi tabanı, phishing veri seti üzerinde fine-tune edildiğinde yüksek performans sağlamaktadır.

**Alt-Kelime Tokenizasyonu:** "PayPaI" (büyük I harfi ile sahte PayPal) gibi typosquatting saldırılarını yakalayabilmektedir.

**Dikkat Mekanizması:** Hangi kelimelerin phishing tespitinde önemli olduğunu öğrenir ("urgent", "verify", "click" gibi).

### 9.3 Hız vs Doğruluk Trade-off

Modeller arasında hız ve doğruluk açısından belirgin trade-off bulunmaktadır:

```
    HIZLI ◄────────────────────────────────► YAVAŞ
       │                                       │
    FastText                                 BERT
     (<1ms)                                 (45ms)
       │                                       │
       ▼                                       ▼
    %90-94 Acc                            %94-97 Acc
               ┌─────────────┐
               │   TF-IDF    │
               │   (25ms)    │
               │ %89.75 Acc  │
               └─────────────┘
```

**Kullanım Senaryosu Önerileri:**

| Senaryo | Önerilen Model | Gerekçe |
|---------|----------------|---------|
| Real-time Email Gateway | FastText | Yüksek throughput gerekli, <1ms gecikme |
| Kritik Güvenlik Analizi | BERT | Doğruluk kritik, gecikme kabul edilebilir |
| Balanced / Genel Kullanım | TF-IDF + RF | İyi denge, açıklanabilirlik (LIME) |
| Ensemble (Production) | Üçü birlikte | En yüksek doğruluk, weighted voting |

### 9.4 False Positive / False Negative Analizi

#### False Positive Senaryoları (Meşru E-posta → Phishing Olarak Yanlış Tespit)

| Senaryo | Açıklama | Mitigation |
|---------|----------|------------|
| Agresif Pazarlama E-postaları | "Limited time offer!", "Act now!" gibi ifadeler | Whitelist domain desteği |
| IT Departmanı Uyarıları | "Your password will expire" gibi sistem mesajları | Threshold ayarı |
| Kısa Mesajlar | Çok kısa mesajlarda model güvensiz olabiliyordu | v2.0'da düzeltildi |

#### False Negative Senaryoları (Phishing → Meşru Olarak Kaçırılan)

| Senaryo | Açıklama | Mitigation |
|---------|----------|------------|
| Hedefli Spear Phishing | Kişiselleştirilmiş, phishing keyword içermeyen saldırılar | Sürekli model eğitimi |
| Zero-Day Phishing | Yeni kampanyalar, eğitim verisinde olmayan pattern'ler | Active learning |
| Homograph Saldırıları | "pаypal.com" (Kiril 'а' karakteri) gibi punycode saldırıları | VirusTotal API, domain age check |

### 9.5 Concept Drift Riski ve Çözüm Stratejileri

**Concept Drift Tanımı:** Phishing saldırıları sürekli evrilmektedir. 2025'te etkili olan phishing pattern'leri 2026'da geçerliliğini yitirebilir.

**Risk Faktörleri:**
- AI tarafından oluşturulan phishing içerikleri (deepfake dahil)
- Yeni sosyal mühendislik teknikleri
- Değişen e-posta formatları ve iletişim stilleri

**Önerilen Stratejiler:**

| Strateji | Açıklama | Periyot |
|----------|----------|---------|
| Periyodik Yeniden Eğitim | Yeni verilerle model güncellemesi | Her 3-6 ayda bir |
| Active Learning | False positive/negative geri bildirimlerden öğrenme | Sürekli |
| Ensemble Çeşitlendirme | Farklı özellik kümelerine dayanan modeller kullanma | Başlangıç tasarımında |
| Sürekli İzleme | Doğruluk metriklerinde düşüş için alerting | Günlük |

---

## 10. API Referansı

Sistem, RESTful API üzerinden tam entegrasyon imkanı sunmaktadır.

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| /api/health | GET | Sistem sağlık kontrolü |
| /api/models/status | GET | Model yükleme durumları |
| /api/email/analyze | POST | TF-IDF ile e-posta analizi |
| /api/email/analyze/bert | POST | BERT ile e-posta analizi |
| /api/email/analyze/fasttext | POST | FastText ile e-posta analizi |
| /api/email/analyze/hybrid | POST | Tüm modeller ile analiz (Ensemble) |
| /api/predict/web | POST | Web log anomali analizi |
| /api/correlation/analyze | GET | Korelasyon analizi |
| /api/dashboard/stats | GET | Dashboard istatistikleri |
| /api/reports/export/excel | GET | Excel dışa aktarma |
| /api/reports/export/json | GET | JSON dışa aktarma |
| /api/settings | GET/POST | Ayarları getir/kaydet |
| /api/demo/generate | POST | Demo veri oluştur |
| /api/database/clear | POST | Verileri temizle |
| /api/virustotal/check-ip/{ip} | GET | VirusTotal IP kontrolü |
| /api/virustotal/check-domain/{domain} | GET | VirusTotal domain kontrolü |

---

## 11. Kurulum ve Yapılandırma

### 11.1 Docker ile Kurulum (Önerilen)

```bash
# 1. Projeyi klonlayın
git clone https://github.com/TheLastKhan/UnifiedCyberThreatDetectionSystem.git
cd UnifiedCyberThreatDetectionSystem

# 2. Docker container'ları başlatın
docker-compose up -d

# 3. Durumu kontrol edin
docker-compose ps

# 4. API sağlık kontrolü
curl http://localhost:5000/api/health
# Beklenen: {"status": "healthy", "version": "1.0.0"}

# 5. Servislere erişin
# Dashboard: http://localhost:5000
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

### 11.2 Docker Container Yapısı

| Container | Port | İşlev | Bağımlılık |
|-----------|------|-------|------------|
| threat-detection-api | 5000 | Flask API + ML Modelleri | db, cache |
| threat-detection-db | 5432 | PostgreSQL Veritabanı | - |
| threat-detection-cache | 6379 | Redis Önbellek | - |
| threat-detection-nginx | 80, 443 | Reverse Proxy, SSL | api |
| threat-detection-prometheus | 9090 | Metrik Toplama | api |
| threat-detection-grafana | 3000 | Görselleştirme Dashboard | prometheus |

### 11.3 Servis Erişim Noktaları

| Servis | URL | Kimlik Bilgileri | Amaç |
|--------|-----|------------------|------|
| Web Dashboard | http://localhost:5000 | Yok | Ana kullanıcı arayüzü |
| Grafana | http://localhost:3000 | admin / admin | Metrik görselleştirme |
| Prometheus | http://localhost:9090 | Yok | Metrik toplama |
| PostgreSQL | localhost:5432 | postgres / postgres | Veritabanı |
| Redis | localhost:6379 | Yok | Önbellek |

### 11.4 Manuel Kurulum (Geliştirme)

```bash
# 1. Virtual environment oluşturun
python -m venv venv

# 2. Aktif edin
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Dashboard'u başlatın
python run_dashboard.py

# 5. Tarayıcıda açın: http://localhost:5000
```

### 11.5 Kurulum Sonrası İlk Adımlar

1. **Demo Veri Oluşturma:** "Generate Demo Data" butonuna tıklayarak örnek tehditler oluşturun
2. **E-posta Analizi Testi:** "Email Analysis" sayfasında bir phishing e-postası gönderin
3. **Web Analizi Testi:** "Web Analysis" sayfasında şüpheli bir log kaydı gönderin
4. **Korelasyon Görüntüleme:** "Correlation Analysis" sayfasında tehdit ilişkilerini inceleyin
5. **Ayarları Özelleştirme:** "Settings" sayfasından tercihleri yapılandırın

---

## 12. Sonuç ve Gelecek Çalışmalar

### 12.1 Sistemin Temel Başarıları

CyberGuard, modern yapay zeka teknolojilerini kullanarak kapsamlı bir siber güvenlik çözümü sunmaktadır:

- **Üç farklı ML modeli** ile yüksek doğrulukta phishing tespiti (ensemble yaklaşım: BERT %50, FastText %30, TF-IDF %20 ağırlıkla)
- **Modüler, servis-odaklı mimari** ile bakım kolaylığı ve bağımsız model geliştirme imkanı
- **Bilinen tasarım kalıpları** (MVC, Event-Driven, Ensemble, Cache-Aside, Factory, Strategy, Façade, Circuit Breaker) ile sağlam altyapı
- **Gerçek zamanlı korelasyon analizi** ile koordineli saldırı tespiti (e-posta + web vektörleri)
- **Trade-off bilinci** ile kullanım senaryosuna uygun model seçimi önerileri
- **Docker ile kolay dağıtım** ve production-ready altyapı (6 container)
- **Açıklanabilir AI (XAI)** - LIME ile model kararlarının görselleştirilmesi
- **Concept drift riski** farkındalığı ve periyodik yeniden eğitim planı

### 12.2 Hedef Kitle ve Ölçeklenebilirlik

Sistem, özellikle orta ölçekli kurumlar (10-100 eşzamanlı kullanıcı) için optimize edilmiştir. Yüksek ölçeklenebilirlik ihtiyacı doğduğunda:
- Horizontal scaling için model inference ayrı container'lara taşınabilir
- TensorFlow Serving veya TorchServe ile dedicated inference server kurulabilir
- Kubernetes ile container orchestration yapılabilir

### 12.3 Gelecek Çalışmalar

- Gerçek zamanlı e-posta gateway entegrasyonu
- Mobil uygulama desteği
- SIEM sistemleri ile entegrasyon
- Active learning pipeline implementasyonu
- Model A/B testing altyapısı
- Multi-tenant mimari desteği

---

**© 2025-2026 CyberGuard Project Team**

---

*Bu rapor, CyberGuard projesinin teknik dokümantasyonu ve akademik değerlendirme amacıyla hazırlanmıştır.*
