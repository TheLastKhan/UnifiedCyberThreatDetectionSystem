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

## 📐 Sistem Mimarisi

Detaylı sistem mimarisi, veri akışı, sınıf diyagramları ve diğer teknik dökümanlar:

- **[Architecture Documentation](docs/architecture.html)** - Tüm diyagramlar (System Architecture, Data Flow, Class Diagram, Sequence Diagram, Component Diagram)

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