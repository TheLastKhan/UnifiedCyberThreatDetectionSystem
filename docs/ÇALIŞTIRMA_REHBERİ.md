# 🚀 ÇALIŞTIRMA REHBERİ - ADIM ADIM

**Unified Cyber Threat Detection System**  
**Son Güncelleme:** 17 Aralık 2025  
**Durum:** ✅ Production Ready

---

## 📋 İÇİNDEKİLER

1. [Hızlı Başlangıç (5 Dakika)](#1-hizli-başlangiç-5-dakika)
2. [Docker Stack Yönetimi](#2-docker-stack-yönetimi)
3. [API Testleri (Email Analizi)](#3-api-testleri-email-analizi)
4. [Database İşlemleri](#4-database-işlemleri)
5. [Monitoring & Dashboard](#5-monitoring--dashboard)
6. [Model Testleri](#6-model-testleri)
7. [Gelişmiş Testler](#7-gelişmiş-testler)
8. [Sorun Giderme](#8-sorun-giderme)

---

## 1. HIZLI BAŞLANGIÇ (5 Dakika)

### Adım 1.1: Docker Stack Durumunu Kontrol Et
```powershell
# Çalışan konteynerları göster
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Beklenen Çıktı:**
```
NAMES                      STATUS              PORTS
threat-detection-api       Up (healthy)        5000/tcp
threat-detection-nginx     Up 3 days           80/tcp, 443/tcp
threat-detection-grafana   Up 3 days (healthy) 3000/tcp
threat-detection-db        Up 3 days (healthy) 5432/tcp
threat-detection-cache     Up 3 days (healthy) 6379/tcp
threat-detection-prometheus Up 3 days (healthy) 9090/tcp
```

✅ **6/6 konteyner çalışıyor olmalı**

---

### Adım 1.2: API Health Check
```powershell
# API'nin sağlıklı olup olmadığını kontrol et
Invoke-WebRequest -Uri http://localhost:5000/api/health -UseBasicParsing
```

**Beklenen Çıktı:**
```
StatusCode: 200
Content: {"status":"healthy","timestamp":"...","version":"1.0.0"}
```

✅ **HTTP 200 OK dönmeli**

---

### Adım 1.3: İlk Email Analizi (TF-IDF)
```powershell
# Basit bir email'i analiz et
$email = @{
    body = 'Hello, this is a weekly newsletter from your company.'
    subject = 'Weekly Newsletter'
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:5000/api/email/analyze `
    -Method POST `
    -Body $email `
    -ContentType "application/json" `
    -UseBasicParsing | 
    Select-Object -ExpandProperty Content | 
    ConvertFrom-Json | 
    Format-List
```

**Beklenen Çıktı:**
```
model_confidence: @{prediction=legitimate; ...}
timestamp: 2025-12-17T...
```

✅ **JSON response dönmeli**

---

### Adım 1.4: BERT ile Email Analizi
```powershell
# BERT modeli ile daha gelişmiş analiz
$email = @{
    body = 'Welcome to our service! We are happy to have you.'
    subject = 'Welcome Email'
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:5000/api/email/analyze-bert `
    -Method POST `
    -Body $email `
    -ContentType "application/json" `
    -UseBasicParsing | 
    Select-Object -ExpandProperty Content | 
    ConvertFrom-Json | 
    Format-List
```

**Beklenen Çıktı:**
```
prediction: legitimate
confidence: 0.99...
model_type: BERT (DistilBERT)
tokens_processed: 15
risk_level: low
```

✅ **BERT analizi başarılı**

---

### Adım 1.5: Grafana Dashboard'u Aç
```powershell
# Grafana monitoring dashboard'u browser'da aç
Start-Process "http://localhost:3000"
```

**Login Bilgileri:**
- Username: `admin`
- Password: `admin`

✅ **Grafana login sayfası açılmalı**

---

## 2. DOCKER STACK YÖNETİMİ

### Adım 2.1: Tüm Konteynerleri Göster
```powershell
# Çalışan ve durmuş tüm konteynerleri listele
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

---

### Adım 2.2: Stack'i Başlat (Eğer Durmuşsa)
```powershell
# Docker Compose ile tüm stack'i başlat
docker-compose up -d
```

**Beklenen Çıktı:**
```
[+] Running 6/6
✔ Container threat-detection-db Created
✔ Container threat-detection-cache Created
...
```

⏱️ **~30-60 saniye sürer**

---

### Adım 2.3: Stack'i Durdur
```powershell
# Tüm konteynerleri durdur (veri kaybolmaz)
docker-compose down
```

**⚠️ DİKKAT:** Database verileri korunur, ancak konteynerler silinir.

---

### Adım 2.4: Belirli Bir Konteyneri Restart Et
```powershell
# Sadece API konteynerini yeniden başlat
docker restart threat-detection-api

# 30 saniye bekle ve health check yap
Start-Sleep -Seconds 30
Invoke-WebRequest -Uri http://localhost:5000/api/health
```

---

### Adım 2.5: Konteyner Loglarını Görüntüle
```powershell
# API loglarını göster (son 50 satır)
docker logs threat-detection-api --tail 50

# Logları canlı takip et (Ctrl+C ile çık)
docker logs threat-detection-api --follow
```

---

### Adım 2.6: Konteyner Kaynak Kullanımı
```powershell
# CPU, Memory kullanımını göster
docker stats --no-stream
```

**Beklenen Çıktı:**
```
CONTAINER               CPU %    MEM USAGE
threat-detection-api    2.5%     500MB
threat-detection-db     1.2%     100MB
...
```

---

## 3. API TESTLERİ (EMAIL ANALİZİ)

### Adım 3.1: Phishing Email Testi (TF-IDF)
```powershell
# Phishing email örneği
$phishing = @{
    body = 'URGENT! Your PayPal account has been suspended. Click here immediately to verify: http://fake-paypal-verify.com'
    subject = 'URGENT: Account Suspended'
    sender = 'security@paypa1.com'
} | ConvertTo-Json

$result = Invoke-WebRequest -Uri http://localhost:5000/api/email/analyze `
    -Method POST `
    -Body $phishing `
    -ContentType "application/json" `
    -UseBasicParsing | 
    Select-Object -ExpandProperty Content | 
    ConvertFrom-Json

# Sonucu güzel göster
Write-Host "`nAnaliz Sonucu:" -ForegroundColor Cyan
Write-Host "Prediction: $($result.model_confidence.prediction)" -ForegroundColor $(if($result.model_confidence.prediction -eq 'phishing'){'Red'}else{'Green'})
Write-Host "Phishing Prob: $([math]::Round($result.model_confidence.phishing_probability*100,1))%"
Write-Host "Model: $($result.model_confidence.model_type)"
```

**Beklenen:** Phishing olarak tespit edilmeli (veya yüksek probability)

---

### Adım 3.2: Legitimate Email Testi (TF-IDF)
```powershell
# Normal, güvenilir email örneği
$legitimate = @{
    body = 'Hello team, this is your weekly company newsletter with updates about our latest products, services, and company news. Best regards, HR Department'
    subject = 'Weekly Newsletter - December 2025'
    sender = 'newsletter@company.com'
} | ConvertTo-Json

$result = Invoke-WebRequest -Uri http://localhost:5000/api/email/analyze `
    -Method POST `
    -Body $legitimate `
    -ContentType "application/json" `
    -UseBasicParsing | 
    Select-Object -ExpandProperty Content | 
    ConvertFrom-Json

Write-Host "`nAnaliz Sonucu:" -ForegroundColor Cyan
Write-Host "Prediction: $($result.model_confidence.prediction)" -ForegroundColor $(if($result.model_confidence.prediction -eq 'legitimate'){'Green'}else{'Red'})
Write-Host "Legitimate Prob: $([math]::Round($result.model_confidence.legitimate_probability*100,1))%"
```

**Beklenen:** Legitimate olarak tespit edilmeli

---

### Adım 3.3: BERT ile Phishing Testi
```powershell
# BERT modeli ile daha detaylı analiz
$phishing_bert = @{
    body = 'CRITICAL SECURITY ALERT! Your bank account has been compromised. Click this link IMMEDIATELY to secure your account: http://malicious-banking-site.com/urgent-verify'
    subject = 'URGENT: Security Breach Detected'
    sender = 'security-alert@fake-bank.com'
} | ConvertTo-Json

$result = Invoke-WebRequest -Uri http://localhost:5000/api/email/analyze-bert `
    -Method POST `
    -Body $phishing_bert `
    -ContentType "application/json" `
    -UseBasicParsing | 
    Select-Object -ExpandProperty Content | 
    ConvertFrom-Json

Write-Host "`n=== BERT Analiz Sonucu ===" -ForegroundColor Cyan
Write-Host "Prediction: $($result.prediction)" -ForegroundColor $(if($result.prediction -eq 'phishing'){'Red'}else{'Yellow'})
Write-Host "Confidence: $([math]::Round($result.confidence*100,1))%"
Write-Host "Phishing Score: $([math]::Round($result.phishing_score*100,2))%"
Write-Host "Risk Level: $($result.risk_level)" -ForegroundColor $(switch($result.risk_level){'low'{'Green'}'medium'{'Yellow'}'high'{'Red'}default{'Red'}})
Write-Host "Tokens: $($result.tokens_processed)"
Write-Host "Model: $($result.model_type)"
```

---

### Adım 3.4: BERT ile Legitimate Testi
```powershell
$legitimate_bert = @{
    body = 'Dear valued customer, we wanted to inform you about our upcoming holiday schedule. Our office will be closed on December 25-26. For urgent matters, please contact our emergency hotline. Happy holidays from our team!'
    subject = 'Holiday Office Schedule'
    sender = 'info@company.com'
} | ConvertTo-Json

$result = Invoke-WebRequest -Uri http://localhost:5000/api/email/analyze-bert `
    -Method POST `
    -Body $legitimate_bert `
    -ContentType "application/json" `
    -UseBasicParsing | 
    Select-Object -ExpandProperty Content | 
    ConvertFrom-Json

Write-Host "`n=== BERT Analiz Sonucu ===" -ForegroundColor Cyan
Write-Host "Prediction: $($result.prediction)" -ForegroundColor Green
Write-Host "Confidence: $([math]::Round($result.confidence*100,1))%"
Write-Host "Risk Level: $($result.risk_level)"
```

---

### Adım 3.5: Model Karşılaştırması (Aynı Email, İki Model)
```powershell
# Test email'i
$test_email = @{
    body = 'WINNER! You have been selected to receive $10,000. Click here to claim your prize: http://lottery-scam.com'
    subject = 'CONGRATULATIONS - You Won!'
} | ConvertTo-Json

Write-Host "`n=== Model Karşılaştırması ===" -ForegroundColor Cyan

# TF-IDF ile test
Write-Host "`n1. TF-IDF Modeli:" -ForegroundColor Yellow
$tfidf = Invoke-WebRequest -Uri http://localhost:5000/api/email/analyze `
    -Method POST -Body $test_email -ContentType "application/json" `
    -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
Write-Host "   Prediction: $($tfidf.model_confidence.prediction)"
Write-Host "   Phishing Prob: $([math]::Round($tfidf.model_confidence.phishing_probability*100,1))%"

# BERT ile test
Write-Host "`n2. BERT Modeli:" -ForegroundColor Yellow
$bert = Invoke-WebRequest -Uri http://localhost:5000/api/email/analyze-bert `
    -Method POST -Body $test_email -ContentType "application/json" `
    -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
Write-Host "   Prediction: $($bert.prediction)"
Write-Host "   Confidence: $([math]::Round($bert.confidence*100,1))%"
Write-Host "   Risk: $($bert.risk_level)"

Write-Host "`n=== Karşılaştırma Özeti ===" -ForegroundColor Cyan
Write-Host "TF-IDF: $($tfidf.model_confidence.prediction) ($([math]::Round($tfidf.model_confidence.phishing_probability*100,1))%)"
Write-Host "BERT: $($bert.prediction) ($([math]::Round($bert.confidence*100,1))%)"
```

---

### Adım 3.6: Batch Email Analizi (Toplu)
```powershell
# Birden fazla email'i aynı anda analiz et
$batch = @{
    emails = @(
        @{body='Phishing attempt 1: Click here to verify account'; subject='Verify Now'},
        @{body='Weekly company newsletter with updates'; subject='Newsletter'},
        @{body='URGENT! Your password expired. Reset now!'; subject='Password Alert'},
        @{body='Meeting reminder for tomorrow at 2pm'; subject='Meeting Reminder'}
    )
} | ConvertTo-Json -Depth 3

$results = Invoke-WebRequest -Uri http://localhost:5000/api/email/batch `
    -Method POST `
    -Body $batch `
    -ContentType "application/json" `
    -UseBasicParsing | 
    Select-Object -ExpandProperty Content | 
    ConvertFrom-Json

Write-Host "`n=== Batch Analiz Sonuçları ===" -ForegroundColor Cyan
Write-Host "Toplam: $($results.count) email"
Write-Host "`nSonuçlar:"
$i = 1
foreach($result in $results.results) {
    Write-Host "`nEmail $i - $($result.subject)"
    Write-Host "  Prediction: $($result.model_confidence.prediction)" -ForegroundColor $(if($result.model_confidence.prediction -eq 'phishing'){'Red'}else{'Green'})
    $i++
}
```

---

## 4. DATABASE İŞLEMLERİ

### Adım 4.1: PostgreSQL'e Bağlan
```powershell
# PostgreSQL shell'e gir (interaktif mod)
docker exec -it threat-detection-db psql -U threat_user -d threat_detection
```

**İçeride kullanabileceğin komutlar:**
```sql
-- Tabloları listele
\dt

-- Tablo yapısını göster
\d threats

-- Çık
\q
```

---

### Adım 4.2: Tabloları Listele (Tek Komut)
```powershell
# Tüm tabloları listele
docker exec threat-detection-db psql -U threat_user -d threat_detection -c "\dt"
```

**Beklenen Çıktı:**
```
List of relations
 Schema |      Name       | Type  |    Owner
--------+-----------------+-------+-------------
 public | threats         | table | threat_user
 public | predictions     | table | threat_user
 public | alerts          | table | threat_user
...
```

---

### Adım 4.3: Threat İstatistikleri
```powershell
# Toplam threat sayısı
docker exec threat-detection-db psql -U threat_user -d threat_detection -c "
SELECT COUNT(*) as total_threats FROM threats;
"
```

---

### Adım 4.4: Son 10 Prediction'ı Göster
```powershell
docker exec threat-detection-db psql -U threat_user -d threat_detection -c "
SELECT 
    id, 
    prediction, 
    confidence, 
    created_at 
FROM predictions 
ORDER BY created_at DESC 
LIMIT 10;
"
```

---

### Adım 4.5: Phishing vs Legitimate Dağılımı
```powershell
docker exec threat-detection-db psql -U threat_user -d threat_detection -c "
SELECT 
    prediction,
    COUNT(*) as count,
    ROUND(AVG(confidence)::numeric, 2) as avg_confidence
FROM predictions
GROUP BY prediction;
"
```

**Beklenen Çıktı:**
```
 prediction | count | avg_confidence
------------+-------+----------------
          0 |   150 |           0.89
          1 |    50 |           0.92
```

---

### Adım 4.6: Database Boyutunu Kontrol Et
```powershell
docker exec threat-detection-db psql -U threat_user -d threat_detection -c "
SELECT 
    pg_size_pretty(pg_database_size('threat_detection')) as database_size;
"
```

---

## 5. MONITORING & DASHBOARD

> **📌 ÖNEMLİ:** Artık **iki farklı dashboard** seçeneğin var:
> 1. **Production (Docker):** Flask API zaten Docker'da çalışıyor → Port 5000
> 2. **Development (Local):** Web dashboard'u local'de çalıştırabilirsin → Port 8050
> 
> Eski usül `python run_dashboard.py` komutu yerine artık Docker kullanıyoruz!

---

### 🌐 HIZLI ERİŞİM TAB LOSU

| Servis | URL | Login | Şifre | Ne İçin? |
|--------|-----|-------|-------|----------|
| **API Dashboard** | http://localhost:5000 | - | - | Email analizi, threat detection |
| **Grafana** | http://localhost:3000 | `admin` | `admin` | Monitoring, grafikler, metrikler |
| **Prometheus** | http://localhost:9090 | - | - | Ham metrikler, PromQL sorguları |
| **Nginx** | http://localhost:80 | - | - | Reverse proxy |
| **Local Dev** | http://localhost:8050 | - | - | Development (manual start gerekli) |

**🔑 Login Notu:**
- Grafana'da **"Email or username"** alanına `admin` yaz
- Prometheus ve API Dashboard'da login gerekmez
- Local Dev (8050) çalışması için `python web_dashboard/app.py` komutu gerekli

---

### 🎯 Hangi Port Ne Zaman Kullanılır?

| Port | Durum | Ne Zaman? |
|------|-------|-----------|
| **5000** | ✅ Zaten çalışıyor | Normal kullanım, her zaman |
| **3000** | ✅ Zaten çalışıyor | Metrik grafikleri görmek için |
| **9090** | ✅ Zaten çalışıyor | Raw metrics sorgulamak için |
| **8050** | ❌ Manuel start | Dashboard'da kod değişikliği yaparken |

---

### SEÇENEK A: Production Dashboard (Docker - Önerilen) 🚀

#### Adım 5.A.1: Docker Dashboard Durumunu Kontrol Et
```powershell
# API konteyneri çalışıyor mu?
docker ps | Select-String "threat-detection-api"
```

**Beklenen Çıktı:**
```
threat-detection-api   Up 3 days (healthy)   0.0.0.0:5000->5000/tcp
```

✅ **Eğer "Up (healthy)" görüyorsan, dashboard zaten çalışıyor demektir!**

---

#### Adım 5.A.2: Dashboard'a Erişim
```powershell
# Browser'da API dashboard'u aç
Start-Process "http://localhost:5000"
```

**🎨 YENİ: Dashboard Artık Dinamik Veriler Gösteriyor!**

Dashboard **artık gerçek veritabanı verilerini** gösteriyor (statik sayılar değil):

**✨ Dinamik Dashboard Özellikleri:**
- ✅ **Gerçek Sistem İstatistikleri** - Veritabanından çekiliyor
- ✅ **Canlı Threat Sayıları** - Son 24 saatteki gerçek tehditler
- ✅ **Email Detection Metrikleri** - Gerçek prediction sayısı ve confidence
- ✅ **Recent Alerts** - Veritabanındaki son 10 tehdit (timestamp ile)
- ✅ **Threat Distribution Chart** - Gerçek veri dağılımı
- ✅ **30 Saniyede Bir Otomatik Güncelleme** - Veriler canlı refresh

**API Endpoint'leri:**
- `http://localhost:5000` - Ana dashboard (dinamik verilerle)
- `http://localhost:5000/api/health` - Health check
- `http://localhost:5000/api/email/analyze` - TF-IDF email analizi
- `http://localhost:5000/api/email/analyze-bert` - BERT email analizi
- `http://localhost:5000/api/dashboard/stats` - Dashboard istatistikleri (**YENİ**)
- `http://localhost:5000/api/dashboard/alerts` - Son tehdit alarmları (**YENİ**)
- `http://localhost:5000/api/dashboard/charts` - Grafik verileri (**YENİ**)

**📊 Dashboard'da Göreceğin Gerçek Veriler:**
```powershell
# Dashboard stats API'sini test et
Invoke-WebRequest -Uri http://localhost:5000/api/dashboard/stats -UseBasicParsing | 
    Select-Object -ExpandProperty Content | 
    ConvertFrom-Json | 
    Format-List
```

**Örnek Çıktı:**
```
system_status      : @{operational=100; models_loaded=true; api_responding=true}
email_detection    : @{accuracy=89.60; roc_auc=96.65; total_predictions=5; phishing_detected=2; avg_confidence=0.87}
web_analysis       : @{features_used=8; total_predictions=0; anomalies_detected=0}
recent_threats     : @{total_24h=2; high_severity=1; phishing=2; anomalies=0}
timestamp          : 2025-12-17T22:13:58.984178
```

**⚠️ ÖNEMLİ: Dashboard Güncellendikten Sonra:**
```powershell
# 1. Container'ı rebuild et (kod değişikliklerini uygular)
docker-compose up -d --build api

# 2. Browser cache'ini temizle - Ctrl+Shift+R (Chrome/Edge) veya Ctrl+F5 (Firefox)
# Yoksa eski statik verileri görmeye devam edersin!
```

---

#### Adım 5.A.3: Dashboard Loglarını İzle
```powershell
# Son 50 satır log göster
docker logs threat-detection-api --tail 50

# Canlı log takibi (Ctrl+C ile çık)
docker logs threat-detection-api --follow
```

---

#### Adım 5.A.4: Dashboard'u Yeniden Başlat
```powershell
# Eğer dashboard sorun çıkarırsa restart et
docker restart threat-detection-api

# 40 saniye bekle (health check için)
Write-Host "Dashboard yeniden başlatılıyor (40 saniye)..." -ForegroundColor Yellow
Start-Sleep -Seconds 40

# Kontrol et
Invoke-WebRequest -Uri http://localhost:5000/api/health -UseBasicParsing
Write-Host "✅ Dashboard hazır!" -ForegroundColor Green
```

---

### SEÇENEK B: Development Dashboard (Local) 💻

> **Ne zaman kullanılır?**
> - Dashboard'da değişiklik yapıp test etmek istersen
> - Docker olmadan çalışmak istersen
> - Debugging için daha detaylı log görmek istersen

#### Adım 5.B.1: Python Environment'ı Aktifleştir
```powershell
# Virtual environment'ı aktifleştir
.\venv\Scripts\Activate.ps1

# Python versiyonunu kontrol et
python --version
# Beklenen: Python 3.10.x veya üzeri
```

---

#### Adım 5.B.2: Gerekli Paketleri Kontrol Et
```powershell
# Flask kurulu mu?
pip list | Select-String "Flask"

# Eğer yoksa yükle
pip install flask gunicorn
```

---

#### Adım 5.B.3: Local Dashboard'u Başlat
```powershell
# Yöntem 1: Flask development server (basit)
python web_dashboard/app.py
```

**Beklenen Çıktı:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:8050
 * Press CTRL+C to quit
```

**Alternatif - Yöntem 2: run_dashboard.py (eski usül)**
```powershell
python run_dashboard.py
```

**Alternatif - Yöntem 3: Gunicorn (production-like)**
```powershell
gunicorn --bind 127.0.0.1:8050 --workers 2 web_dashboard.app:app
```

---

#### Adım 5.B.4: Local Dashboard'a Erişim
```powershell
# Browser'da local dashboard'u aç
Start-Process "http://localhost:8050"
```

**Port Farkları:**
- **5000:** Docker production API
- **8050:** Local development dashboard

**⚠️ SORUN GİDERME:**
Eğer **"Bu siteye ulaşılamıyor"** hatası alırsan:
```powershell
# 1. Local dashboard çalışıyor mu kontrol et
Get-Process | Where-Object {$_.ProcessName -eq "python" -or $_.ProcessName -eq "gunicorn"}

# 2. Port 8050 kullanımda mı?
netstat -ano | Select-String ":8050"

# 3. Eğer çalışmıyorsa tekrar başlat
python web_dashboard/app.py
```

---

#### Adım 5.B.5: Local Dashboard'u Durdur
```
Ctrl + C tuşlarına bas
```

Veya PowerShell'de:
```powershell
# Flask process'ini bul ve sonlandır
$flask = Get-Process | Where-Object {$_.ProcessName -like "*python*"}
$flask | Stop-Process -Force
```

---

### Adım 5.1: Grafana Monitoring Dashboard'u Aç
```powershell
# Browser'da Grafana'yı aç
Start-Process "http://localhost:3000"
```

**📌 Login Bilgileri (ÖNEMLİ!):**
- **Email or Username:** `admin`
- **Password:** `admin`

**İlk Giriş Adımları:**
1. Browser'da `http://localhost:3000/login` açılacak
2. **Email or username** alanına: `admin` yaz
3. **Password** alanına: `admin` yaz
4. **Log in** butonuna tıkla
5. İlk girişte şifre değiştirmeni isteyebilir:
   - **Skip** butonuna basabilirsin (opsiyonel)
   - Veya yeni şifre belirleyebilirsin

**Ne görürsün?**
- API request metrics (toplam request sayısı)
- Response time graphs (yanıt süreleri)
- Error rates (hata oranları)
- System resource usage (CPU, Memory kullanımı)

**Dashboard Kullanımı:**
```powershell
# Grafana'da dashboard oluşturmak için:
# 1. Sol menüden "Dashboards" > "New Dashboard"
# 2. "Add new panel" tıkla
# 3. Data source olarak "Prometheus" seç
# 4. Metric seç ve kaydet
```

---

### Adım 5.2: Prometheus Metrics (Nasıl Çalışır?)
```powershell
# Prometheus UI'ı aç
Start-Process "http://localhost:9090"
```

**🔍 Prometheus Nedir?**
Prometheus, sistem ve uygulama metriklerini toplayan ve sorgulayan bir monitoring sistemidir.

**📊 Nasıl Kullanılır:**

#### 1. Basit Metric Sorgulama
```
1. Browser'da http://localhost:9090 aç
2. Üstteki arama kutusuna metric adı yaz
3. "Execute" butonuna tıkla
4. "Graph" veya "Table" sekmesinde sonuçları gör
```

#### 2. Örnek Query'ler (Direkt Kopyala-Yapıştır)

**Sistem Durumu:**
```promql
# Tüm konteynerler çalışıyor mu?
up
```

**API Performans:**
```promql
# Son 5 dakika içinde toplam request
sum(rate(http_requests_total[5m]))

# Ortalama response time
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
```

**Resource Kullanımı:**
```promql
# CPU kullanımı (saniye)
process_cpu_seconds_total

# Memory kullanımı (bytes)
go_memstats_alloc_bytes

# Memory kullanımı (MB - daha okunabilir)
go_memstats_alloc_bytes / 1024 / 1024
```

**Docker Konteynerleri:**
```promql
# Container CPU kullanımı
rate(container_cpu_usage_seconds_total[5m])

# Container Memory kullanımı
container_memory_usage_bytes / 1024 / 1024
```

#### 3. Advanced Query Örneği
```promql
# Son 1 saatte API error rate (%)
sum(rate(http_requests_total{status=~"5.."}[1h])) / sum(rate(http_requests_total[1h])) * 100
```

**💡 İpuçları:**
- Prometheus sadece metrics saklar, grafikler için Grafana kullan
- `/targets` sayfasında hangi servislerin izlendiğini görebilirsin
- `/alerts` sayfasında aktif alarmları görebilirsin

---

### Adım 5.3: API Swagger Documentation
```powershell
# API dokümantasyonunu aç (eğer FastAPI çalışıyorsa)
Start-Process "http://localhost:5000/docs"
```

**Not:** Eğer 404 alırsan, FastAPI çalışmıyor demektir (Flask çalışıyor)

---

### Adım 5.4: Nginx Status
```powershell
# Nginx'in çalıştığını kontrol et
Invoke-WebRequest -Uri http://localhost:80 -UseBasicParsing
```

---

### Adım 5.5: Dashboard Port Kontrolü
```powershell
# Hangi portlar kullanımda?
Write-Host "`n=== Port Kullanımı ===" -ForegroundColor Cyan
netstat -ano | Select-String ":5000|:8050|:3000|:9090|:80" | ForEach-Object {
    $line = $_.Line
    if($line -match ":5000") { Write-Host "5000 (Docker API): $line" -ForegroundColor Green }
    if($line -match ":8050") { Write-Host "8050 (Local Dashboard): $line" -ForegroundColor Yellow }
    if($line -match ":3000") { Write-Host "3000 (Grafana): $line" -ForegroundColor Cyan }
    if($line -match ":9090") { Write-Host "9090 (Prometheus): $line" -ForegroundColor Blue }
    if($line -match ":80") { Write-Host "80 (Nginx): $line" -ForegroundColor Magenta }
}
```

---

### Adım 5.6: Tüm Dashboard'ları Aç (Tek Komut)
```powershell
# Tüm monitoring arayüzlerini browser'da aç
Write-Host "`nTüm dashboard'lar açılıyor..." -ForegroundColor Cyan
Start-Process "http://localhost:5000"        # Docker API
Start-Process "http://localhost:3000"        # Grafana
Start-Process "http://localhost:9090"        # Prometheus
Write-Host "✅ Dashboard'lar açıldı!" -ForegroundColor Green
```

---

### 🎯 Hangi Dashboard'u Kullanmalıyım?

| Senaryo | Kullan |
|---------|--------|
| **Normal kullanım, production test** | Docker (Port 5000) ✅ |
| **Dashboard kodunda değişiklik yapıyorum** | Local (Port 8050) |
| **Monitoring, metrikler görüntüleme** | Grafana (Port 3000) |
| **Ham metrics, PromQL sorguları** | Prometheus (Port 9090) |
| **Hızlı geliştirme, debugging** | Local (Port 8050) |

**Öneri:** Çoğu zaman **Docker (Port 5000)** kullan, çünkü:
- ✅ Zaten çalışıyor (docker-compose up ile)
- ✅ Production ortamını simüle ediyor
- ✅ Gunicorn ile optimize edilmiş
- ✅ Nginx reverse proxy ile korumalı

---

### ⚠️ Sorun Giderme

#### "Port 5000 already in use" Hatası
```powershell
# Hangi process port 5000'i kullanıyor?
netstat -ano | Select-String ":5000"

# Eğer Docker ise - normal, zaten çalışıyor
# Eğer başka bir process ise - sonlandır veya farklı port kullan
```

#### "Connection refused" Hatası
```powershell
# Docker konteyneri çalışıyor mu?
docker ps | Select-String "threat-detection-api"

# Eğer çalışmıyorsa başlat
docker-compose up -d api
Start-Sleep -Seconds 40
```

#### Local dashboard çalışmıyor
```powershell
# Python environment aktif mi?
python --version

# Flask kurulu mu?
pip list | Select-String "Flask"

# Eğer yoksa
pip install -r requirements.txt
```

#### Dashboard'da CSS sorunları (Yazılar çakışıyor, sidebar arkasında kalıyor)

**ADIM 1: Docker Container'ı Rebuild Et**
```powershell
# CSS değişikliklerini Docker'a uygula (2-3 dakika sürer)
docker-compose up -d --build api

# 40 saniye bekle (health check)
Start-Sleep -Seconds 40

# API sağlıklı mı kontrol et
Invoke-WebRequest -Uri http://localhost:5000/api/health -UseBasicParsing
```

**ADIM 2: Browser Cache'i Temizle (ÇOK ÖNEMLİ!)**

Bu adımı yapmazsan eski CSS'i görmeye devam edersin!

**Yöntem 1: Hard Refresh (En Hızlı) ⚡**
```
Dashboard açıkken:
• Chrome/Edge: Ctrl + Shift + R
• Firefox: Ctrl + F5  
• Safari: Cmd + Shift + R
```

**Yöntem 2: Developer Tools ile 🔧**
```
1. F12 bas (Developer Tools aç)
2. Network sekmesine git
3. "Disable cache" checkbox'ını işaretle
4. F5 ile sayfayı yenile
5. Developer Tools'u açık tut (kapatırsan cache devreye girer)
```

**Yöntem 3: Manuel Cache Temizleme 🗑️**
```
Chrome/Edge:
1. Ctrl + Shift + Delete
2. "Cached images and files" seç
3. "Clear data"

Firefox:
1. Ctrl + Shift + Delete
2. "Cache" seç
3. "Clear Now"
```

**Yöntem 4: Tam Reset (En Garantili) 🔄**
```powershell
# Browser'ı tamamen kapat
# PowerShell'den tekrar aç ve cache'siz başlat:
Start-Process chrome.exe --incognito "http://localhost:5000"
# veya
Start-Process firefox.exe -private-window "http://localhost:5000"
```

**✅ CSS Sorunları Düzeltildi (Rebuild + Cache Temizleme sonrası):**
- ✅ Header yazıları artık çakışmıyor
- ✅ Form elementleri sidebar'ın arkasında kalmıyor
- ✅ Input, label, button'lar düzgün görünüyor
- ✅ Loading animasyonları doğru pozisyonda
- ✅ Request count ve error rate metrikleri görünür
- ✅ Tüm card'lar sidebar'ın sağında düzgün konumlanmış

---

## 6. MODEL TESTLERİ

### Adım 6.1: Model Dosyalarını Kontrol Et
```powershell
# Tüm model dosyalarını listele
Get-ChildItem models\ -Recurse | 
    Select-Object Name, @{N='Size(MB)';E={[math]::Round($_.Length/1MB,2)}} |
    Sort-Object Name
```

**Beklenen Dosyalar:**
```
bert_finetuned/
├── config.json
├── model.safetensors (260MB)
├── vocab.txt
├── tokenizer_config.json
├── special_tokens_map.json
└── training_args.bin

email_detector_stacking.pkl
email_detector_voting.pkl
tfidf_vectorizer.pkl
fasttext_email_detector.bin (885MB)
web_anomaly_detector.pkl
log_scaler.pkl
```

---

### Adım 6.2: BERT Model Bilgilerini Göster
```powershell
# BERT model config'ini oku
Get-Content models\bert_finetuned\config.json | ConvertFrom-Json | Format-List
```

**Çıktı:**
```
model_type: distilbert
num_labels: 2
hidden_size: 768
num_attention_heads: 12
...
```

---

### Adım 6.3: Model Boyutları
```powershell
Write-Host "`n=== Model Boyutları ===" -ForegroundColor Cyan

$models = @{
    "TF-IDF Vectorizer" = "models\tfidf_vectorizer.pkl"
    "Stacking Model" = "models\email_detector_stacking.pkl"
    "Voting Model" = "models\email_detector_voting.pkl"
    "BERT Model" = "models\bert_finetuned\model.safetensors"
    "FastText Model" = "models\fasttext_email_detector.bin"
}

foreach($name in $models.Keys) {
    $file = $models[$name]
    if(Test-Path $file) {
        $size = [math]::Round((Get-Item $file).Length/1MB, 2)
        Write-Host "$name : $size MB" -ForegroundColor Green
    } else {
        Write-Host "$name : BULUNAMADI" -ForegroundColor Red
    }
}
```

---

## 7. GELİŞMİŞ TESTLER

### Adım 7.1: Performance Benchmarking
```powershell
Write-Host "`n=== Performance Benchmark ===" -ForegroundColor Cyan

$email = @{body='Test email for benchmarking'} | ConvertTo-Json

# TF-IDF benchmark (10 request)
Write-Host "`n1. TF-IDF Performance:" -ForegroundColor Yellow
$tfidf_times = @()
for($i=1; $i -le 10; $i++) {
    $start = Get-Date
    Invoke-WebRequest -Uri http://localhost:5000/api/email/analyze `
        -Method POST -Body $email -ContentType "application/json" `
        -UseBasicParsing | Out-Null
    $elapsed = (Get-Date) - $start
    $tfidf_times += $elapsed.TotalMilliseconds
}
$tfidf_avg = ($tfidf_times | Measure-Object -Average).Average
Write-Host "   Ortalama: $([math]::Round($tfidf_avg, 2)) ms"

# BERT benchmark (5 request - daha yavaş)
Write-Host "`n2. BERT Performance:" -ForegroundColor Yellow
$bert_times = @()
for($i=1; $i -le 5; $i++) {
    $start = Get-Date
    Invoke-WebRequest -Uri http://localhost:5000/api/email/analyze-bert `
        -Method POST -Body $email -ContentType "application/json" `
        -UseBasicParsing | Out-Null
    $elapsed = (Get-Date) - $start
    $bert_times += $elapsed.TotalMilliseconds
}
$bert_avg = ($bert_times | Measure-Object -Average).Average
Write-Host "   Ortalama: $([math]::Round($bert_avg, 2)) ms"

Write-Host "`n=== Karşılaştırma ===" -ForegroundColor Cyan
Write-Host "TF-IDF: $([math]::Round($tfidf_avg, 0)) ms"
Write-Host "BERT: $([math]::Round($bert_avg, 0)) ms"
Write-Host "BERT $([math]::Round($bert_avg/$tfidf_avg, 1))x daha yavaş"
```

---

### Adım 7.2: Stress Test (100 Request)
```powershell
Write-Host "`n=== Stress Test (100 requests) ===" -ForegroundColor Cyan

$email = @{body='Stress test email'} | ConvertTo-Json
$success = 0
$failed = 0
$start_time = Get-Date

for($i=1; $i -le 100; $i++) {
    try {
        Invoke-WebRequest -Uri http://localhost:5000/api/email/analyze `
            -Method POST -Body $email -ContentType "application/json" `
            -UseBasicParsing | Out-Null
        $success++
    } catch {
        $failed++
    }
    
    if($i % 10 -eq 0) {
        Write-Host "Progress: $i/100" -ForegroundColor Yellow
    }
}

$total_time = (Get-Date) - $start_time
Write-Host "`nSonuç:" -ForegroundColor Cyan
Write-Host "Başarılı: $success"
Write-Host "Başarısız: $failed"
Write-Host "Toplam Süre: $([math]::Round($total_time.TotalSeconds, 2)) saniye"
Write-Host "Request/saniye: $([math]::Round(100/$total_time.TotalSeconds, 2))"
```

---

### Adım 7.3: Çeşitli Email Türleri Testi
```powershell
Write-Host "`n=== Çeşitli Email Türleri ===" -ForegroundColor Cyan

$test_cases = @(
    @{name='Nigerian Scam'; body='Dear friend, I am a prince from Nigeria...'},
    @{name='Banking Phishing'; body='Your bank account is locked. Verify now: http://fake-bank.com'},
    @{name='Lottery Scam'; body='CONGRATULATIONS! You won $1,000,000. Claim now!'},
    @{name='Password Reset'; body='Click here to reset your password: http://malicious-site.com'},
    @{name='Invoice Scam'; body='Invoice due. Pay now: http://fake-invoice.com'},
    @{name='Work Email'; body='Meeting scheduled for tomorrow at 10am in room 301'},
    @{name='Newsletter'; body='Weekly tech news: Latest in AI, Cloud Computing, and more'},
    @{name='HR Email'; body='Reminder: Submit your timesheet by end of day Friday'}
)

foreach($test in $test_cases) {
    $email = @{body=$test.body} | ConvertTo-Json
    $result = Invoke-WebRequest -Uri http://localhost:5000/api/email/analyze-bert `
        -Method POST -Body $email -ContentType "application/json" `
        -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
    
    Write-Host "`n$($test.name):" -ForegroundColor Yellow
    Write-Host "  Prediction: $($result.prediction)" -ForegroundColor $(if($result.prediction -eq 'phishing'){'Red'}else{'Green'})
    Write-Host "  Confidence: $([math]::Round($result.confidence*100,1))%"
    Write-Host "  Risk: $($result.risk_level)"
}
```

---

## 8. SORUN GİDERME

### Adım 8.1: API Yanıt Vermiyor
```powershell
# 1. Konteyner çalışıyor mu?
docker ps | Select-String "threat-detection-api"

# 2. Logları kontrol et
docker logs threat-detection-api --tail 30

# 3. Health check
Invoke-WebRequest -Uri http://localhost:5000/api/health

# 4. Restart et
docker restart threat-detection-api
Start-Sleep -Seconds 40
Invoke-WebRequest -Uri http://localhost:5000/api/health
```

---

### Adım 8.2: Database Bağlantı Hatası
```powershell
# 1. Database konteyneri çalışıyor mu?
docker ps | Select-String "threat-detection-db"

# 2. Bağlantı testi
docker exec threat-detection-db psql -U threat_user -d threat_detection -c "\l"

# 3. Restart et
docker restart threat-detection-db
Start-Sleep -Seconds 20
```

---

### Adım 8.3: Port Kullanımda Hatası
```powershell
# 1. Hangi process port 5000'i kullanıyor?
netstat -ano | Select-String ":5000"

# 2. Process'i sonlandır (PID'yi yukarıdan al)
# Stop-Process -Id <PID> -Force

# 3. Veya tüm stack'i restart et
docker-compose down
docker-compose up -d
```

---

### Adım 8.4: BERT Model Yüklenemedi
```powershell
# 1. Model dosyaları var mı?
Get-ChildItem models\bert_finetuned\

# Beklenen: 6 dosya (config.json, model.safetensors, vocab.txt, etc.)

# 2. Dosya boyutları doğru mu?
$model_file = "models\bert_finetuned\model.safetensors"
if(Test-Path $model_file) {
    $size_mb = [math]::Round((Get-Item $model_file).Length/1MB, 2)
    Write-Host "Model boyutu: $size_mb MB" -ForegroundColor Green
    if($size_mb -lt 200) {
        Write-Host "HATA: Model dosyası çok küçük!" -ForegroundColor Red
    }
} else {
    Write-Host "HATA: Model dosyası bulunamadı!" -ForegroundColor Red
}

# 3. API loglarını kontrol et
docker logs threat-detection-api | Select-String "BERT"
```

---

### Adım 8.5: Tüm Sistemi Reset Et
```powershell
Write-Host "⚠️ DİKKAT: Bu işlem tüm stack'i durdurup yeniden başlatacak!" -ForegroundColor Red
Write-Host "Verileri KAYDETMEZ. Devam etmek için ENTER'a bas, iptal için Ctrl+C..."
Read-Host

# 1. Tüm konteynerleri durdur
docker-compose down

# 2. Volumes'leri temizle (OPSİYONEL - veriler silinir!)
# docker-compose down -v

# 3. Yeniden başlat
docker-compose up -d

# 4. 60 saniye bekle
Write-Host "Konteynerler başlatılıyor (60 saniye)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# 5. Health check
Invoke-WebRequest -Uri http://localhost:5000/api/health

Write-Host "`n✅ Reset tamamlandı!" -ForegroundColor Green
```

---

## 9. HIZLI TEST SCRIPT'Leri

### Script 9.1: Komple Sistem Testi (Tek Komut)
```powershell
# KOMPLE_TEST.ps1 - Her şeyi test et
Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   KOMPLE SİSTEM TESTİ                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Cyan

# 1. Docker
Write-Host "1. Docker Stack:" -ForegroundColor Yellow
$containers = docker ps --filter "name=threat-detection" --format "{{.Names}}" | Measure-Object -Line
Write-Host "   ✓ $($containers.Lines)/6 konteyner çalışıyor" -ForegroundColor Green

# 2. API Health
Write-Host "`n2. API Health Check:" -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri http://localhost:5000/api/health -UseBasicParsing
    Write-Host "   ✓ API sağlıklı (HTTP $($health.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "   ✗ API yanıt vermiyor!" -ForegroundColor Red
}

# 3. Database
Write-Host "`n3. PostgreSQL:" -ForegroundColor Yellow
try {
    $tables = docker exec threat-detection-db psql -U threat_user -d threat_detection -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"
    Write-Host "   ✓ Database çalışıyor ($tables tablo)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Database bağlantı hatası!" -ForegroundColor Red
}

# 4. TF-IDF Test
Write-Host "`n4. TF-IDF Email Analizi:" -ForegroundColor Yellow
try {
    $email = @{body='Test email'} | ConvertTo-Json
    $result = Invoke-WebRequest -Uri http://localhost:5000/api/email/analyze -Method POST -Body $email -ContentType "application/json" -UseBasicParsing
    Write-Host "   ✓ TF-IDF çalışıyor" -ForegroundColor Green
} catch {
    Write-Host "   ✗ TF-IDF hatası: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. BERT Test
Write-Host "`n5. BERT Email Analizi:" -ForegroundColor Yellow
try {
    $email = @{body='Test email'; subject='Test'} | ConvertTo-Json
    $result = Invoke-WebRequest -Uri http://localhost:5000/api/email/analyze-bert -Method POST -Body $email -ContentType "application/json" -UseBasicParsing
    Write-Host "   ✓ BERT çalışıyor" -ForegroundColor Green
} catch {
    Write-Host "   ✗ BERT hatası: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. Grafana
Write-Host "`n6. Grafana Dashboard:" -ForegroundColor Yellow
try {
    $grafana = Invoke-WebRequest -Uri http://localhost:3000 -UseBasicParsing -Method Head
    Write-Host "   ✓ Grafana erişilebilir (HTTP $($grafana.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Grafana erişilemiyor!" -ForegroundColor Red
}

Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   TEST TAMAMLANDI                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Cyan
```

---

### Script 9.2: Model Performans Karşılaştırma
```powershell
# MODEL_COMPARISON.ps1
Write-Host "`n=== MODEL PERFORMANS KARŞILAŞTIRMASI ===" -ForegroundColor Cyan

$test_email = @{
    body = 'URGENT! Win $50,000 now. Click: http://lottery-scam.com'
    subject = 'YOU WON!'
} | ConvertTo-Json

Write-Host "`nTest Email: URGENT! Win $50,000 now..." -ForegroundColor Yellow

# TF-IDF
Write-Host "`n1. TF-IDF Model:" -ForegroundColor Cyan
$start = Get-Date
$tfidf = Invoke-WebRequest -Uri http://localhost:5000/api/email/analyze `
    -Method POST -Body $test_email -ContentType "application/json" `
    -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
$tfidf_time = ((Get-Date) - $start).TotalMilliseconds
Write-Host "   Prediction: $($tfidf.model_confidence.prediction)"
Write-Host "   Confidence: $([math]::Round($tfidf.model_confidence.phishing_probability*100,1))%"
Write-Host "   Time: $([math]::Round($tfidf_time, 0)) ms"

# BERT
Write-Host "`n2. BERT Model:" -ForegroundColor Cyan
$start = Get-Date
$bert = Invoke-WebRequest -Uri http://localhost:5000/api/email/analyze-bert `
    -Method POST -Body $test_email -ContentType "application/json" `
    -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
$bert_time = ((Get-Date) - $start).TotalMilliseconds
Write-Host "   Prediction: $($bert.prediction)"
Write-Host "   Confidence: $([math]::Round($bert.confidence*100,1))%"
Write-Host "   Time: $([math]::Round($bert_time, 0)) ms"

Write-Host "`n=== ÖZET ===" -ForegroundColor Cyan
Write-Host "TF-IDF: $($tfidf.model_confidence.prediction) ($([math]::Round($tfidf_time,0))ms)"
Write-Host "BERT: $($bert.prediction) ($([math]::Round($bert_time,0))ms)"
Write-Host "`nBERT $([math]::Round($bert_time/$tfidf_time,1))x daha yavaş ama daha doğru"
```

---

## 📝 NOTLAR VE İPUÇLARI

### 🎯 Önemli Noktalar:

1. **Docker Stack başlatma süresi:** ~60 saniye (health check'ler için)
2. **API restart sonrası bekleme:** ~40 saniye
3. **BERT inference:** ~500-800ms (CPU), GPU ile ~50-100ms olur
4. **TF-IDF inference:** ~50-100ms
5. **Database backup:** docker volumes kullanıyor, `docker-compose down -v` dikkatli kullan!

### 🔍 Hata Ayıklama:

- **"Connection refused"** → Konteyner çalışmıyor, `docker ps` kontrol et
- **"404 Not Found"** → Endpoint yanlış veya Flask/FastAPI karışması
- **"500 Internal Server Error"** → `docker logs` kontrol et
- **"Model not found"** → BERT model dosyaları eksik, `models/bert_finetuned/` kontrol et

### 📊 Beklenen Performans:

| Metrik | Değer |
|--------|-------|
| API Response (TF-IDF) | 50-150ms |
| API Response (BERT) | 500-800ms |
| Throughput (TF-IDF) | ~20 req/sec |
| Throughput (BERT) | ~2 req/sec |
| Memory (API) | ~500MB |
| Memory (DB) | ~100MB |

### 🚀 Production Tips:

1. **SSL/TLS:** Nginx ile HTTPS kullan (production için)
2. **Rate Limiting:** API koruması için aktifleştir
3. **Backup:** PostgreSQL database'i düzenli yedekle
4. **Monitoring:** Grafana dashboard'larını özelleştir
5. **Logging:** ELK stack ekle (opsiyonel)

---

## 🎊 HIZLI BAŞLANGIÇ ÖZETİ

En temel testler için bu 5 komutu çalıştır:

```powershell
# 1. Docker durumu
docker ps --filter "name=threat-detection"

# 2. API health
Invoke-WebRequest -Uri http://localhost:5000/api/health

# 3. TF-IDF test
$e = @{body='Test email'} | ConvertTo-Json; Invoke-WebRequest -Uri http://localhost:5000/api/email/analyze -Method POST -Body $e -ContentType "application/json"

# 4. BERT test
$e = @{body='Test email'} | ConvertTo-Json; Invoke-WebRequest -Uri http://localhost:5000/api/email/analyze-bert -Method POST -Body $e -ContentType "application/json"

# 5. Grafana aç
Start-Process "http://localhost:3000"
```

---

**🎉 İyi testler! Sorular için:** [TEST_RAPORU.md](TEST_RAPORU.md) ve [SORUN_GIDERME_RAPORU.md](SORUN_GIDERME_RAPORU.md) dosyalarına bak.

**Son Güncelleme:** 17 Aralık 2025  
**Durum:** ✅ Production Ready  
**Versiyon:** 1.0.0
