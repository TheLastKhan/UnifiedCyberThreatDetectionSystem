# 🛡️ Unified Cyber Threat Detection Platform

AI-Powered Email & Web Security Analysis with Explainable AI

## 🎯 Proje Hakkında

Bu proje, email phishing tespiti ve web log analizini birleştirerek kapsamlı bir siber güvenlik tehdidi tespit sistemi oluşturur.

### Özellikler

- 📧 **Email Phishing Detection:** NLP ve ML tabanlı phishing tespiti
- 🌐 **Web Log Analysis:** Anomaly detection ile saldırı tespiti
- 🔗 **Cross-Platform Correlation:** İki platform arası tehdit korelasyonu
- 🧠 **Explainable AI:** LIME ve SHAP ile açıklanabilir AI
- 📊 **Interactive Dashboard:** Flask tabanlı web arayüzü

## 📐 Teknik Dokümantasyon

### Sistem Mimarisi
Detaylı sistem mimarisi, veri akışı, sınıf diyagramları ve diğer teknik dökümanlar:
- **[Architecture Documentation](docs/architecture.html)** - Tüm diyagramlar (System Architecture, Data Flow, Class Diagram, Sequence Diagram, Component Diagram)

### API Documentation
REST API'nin detaylı dokümantasyonu, endpoint'leri, request/response örnekleri:
- **[Interactive API Documentation (Swagger UI)](docs/api.html)** - Tüm endpoint'ler, parametreler, response'lar
- **[OpenAPI Specification](docs/openapi.yaml)** - OpenAPI 3.1.0 formatında tam specification
- **[API Examples](docs/API_EXAMPLES.md)** - cURL ve Python örnekleri

### Kullanım Rehberleri
Sistemin gerçek dünya senaryolarında nasıl kullanılacağına dair kapsamlı kılavuzlar:
- **[Usage Scenarios & Tutorials](docs/USAGE_SCENARIOS.md)** - 5 detaylı senaryo (Phishing Campaign, Web Attack, Coordinated Attack, Model Training, Dashboard Integration)
- **[Best Practices Guide](docs/BEST_PRACTICES.md)** - Veri hazırlığı, model eğitimi, deployment checklist, troubleshooting

### Database & Persistence
Veri depolaması ve analitik için PostgreSQL entegrasyonu:
- **[Database Integration Guide](docs/FAZ4_DATABASE.md)** - SQLAlchemy ORM modelleri, bağlantı yönetimi, CSV import, 17 test (✅ 100% passing)
- **Models**: Email, WebLog, ThreatCorrelation, ThreatReport, AuditLog
- **Features**: Connection pooling, transaction safety, batch import (4500+ emails), comprehensive queries

### Deployment & Operations
Production ortamına deploy etmek için kapsamlı kılavuzlar:
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Docker, Nginx, SSL/TLS, Monitoring, Backup, Production Checklist
- **[Dockerfile](Dockerfile)** - Production-ready Docker image
- **[docker-compose.yml](docker-compose.yml)** - Full stack (API, Database, Cache, Nginx, Monitoring)
- **[.env.example](.env.example)** - Environment configuration template

### Hızlı Genel Bakış

```
User Input (Email + Web Logs)
         ↓
    ┌────┴────┐
    ↓         ↓
Email      Web
Detector   Analyzer
    ↓         ↓
    └────┬────┘
         ↓
Correlation Engine
         ↓
Unified Platform
         ↓
Report + Dashboard
```

## 🚀 Kurulum

### Gereksinimler

- Python 3.8+
- pip
- Virtual environment (önerilen)

### Adımlar

1. Repository'yi klonla:
```bash
git clone <repo-url>
cd unified_threat_detection