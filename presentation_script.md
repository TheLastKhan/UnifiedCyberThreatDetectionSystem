# CyberGuard Sunum Scripti
## 10 Dakikalık Sunum - 3 Kişi İçin Bölünmüş

---

# 👤 PRESENTER 1 (Slides 1-7) - Yaklaşık 3.5 dakika

## Slide 1: Title (30 saniye)
"Merhaba hocam, bugün size CyberGuard projesini sunacağız. CyberGuard, yapay zeka destekli birleşik siber tehdit tespit platformudur. E-posta phishing tespiti ve web log anomali analizini açıklanabilir AI ile birleştiren enterprise seviyesinde bir güvenlik çözümü geliştirdik."

## Slide 2: Problem Statement (45 saniye)
"Günümüzde üç temel güvenlik sorunu var:

Birincisi, e-posta ve web güvenlik sistemleri birbirinden izole çalışıyor. Koordineli saldırılar tespit edilemiyor.

İkincisi, ML modelleri kararlarını açıklamıyor. Güvenlik analistleri 'kara kutu' sonuçlara güvenemiyor.

Üçüncüsü, geleneksel imza tabanlı sistemler sadece bilinen tehditleri tespit ediyor.

SlashNext 2024 raporuna göre phishing saldırıları yüzde 202 arttı. Bu ciddi bir problem."

## Slide 3: Solution Overview (40 saniye)
"CyberGuard bu problemleri şöyle çözüyor:

Üç farklı AI modeli ile e-posta phishing tespiti yapıyoruz - BERT, FastText ve TF-IDF.

Isolation Forest ile web log anomali tespiti gerçekleştiriyoruz.

LIME ile açıklanabilir AI entegrasyonu sağladık - model neden bu kararı verdi sorusuna cevap verebiliyoruz.

Birleşik risk skorlama sistemi ile 0-100 arası risk puanı hesaplıyoruz."

## Slide 4: System Architecture (40 saniye)
"Sistemimiz dört katmanlı bir mimariye sahip:

Presentation katmanında Flask web uygulaması ve REST API var.

ML Analysis katmanında BERT, FastText, TF-IDF modelleri ve LIME explainer bulunuyor.

Integration katmanında korelasyon motoru ve risk hesaplayıcı yer alıyor.

Data katmanında PostgreSQL veritabanı ve Redis cache kullanıyoruz.

MVC, Event-Driven, Ensemble gibi sekiz farklı design pattern uyguladık."

## Slide 5: BERT Model (30 saniye)
"En yüksek doğruluğa sahip modelimiz BERT - yüzde 94-97 accuracy.

DistilBERT kullanıyoruz, 66 milyon parametre var.

Bağlamı anlıyor - 'hesabınızı doğrulayın' gibi şüpheli kalıpları yakalıyor.

Typo'ları bile algılıyor - Paypa1 yazılsa bile PayPal olarak anlıyor."

## Slide 6: FastText Model (25 saniye)
"FastText en hızlı modelimiz - 1 milisaniyenin altında inference süresi.

Yüzde 90-94 accuracy sağlıyor.

Saatte milyonlarca e-posta işleyebilir.

Gerçek zamanlı yüksek hacimli işleme için ideal."

## Slide 7: TF-IDF Model (25 saniye)
"TF-IDF modelimiz açıklanabilirlik için en uygun model.

Yüzde 89.75 accuracy, ROC-AUC yüzde 97.50.

LIME ile mükemmel uyum sağlıyor.

Hangi kelimelerin tespiti tetiklediğini gösterebiliyoruz."

---

# 👤 PRESENTER 2 (Slides 8-13) - Yaklaşık 3.5 dakika

## Slide 8: Ensemble Approach (35 saniye)
"Üç modeli birleştirerek ensemble yaklaşımı kullanıyoruz.

Formülümüz: BERT çarpı 0.5, artı FastText çarpı 0.3, artı TF-IDF çarpı 0.2.

BERT'e en yüksek ağırlığı verdik çünkü en doğru sonuçları veriyor.

Bu kombinasyonla yüzde 97.1 accuracy elde ettik - tek başına herhangi bir modelden daha iyi."

## Slide 9: Model Comparison Table (30 saniye)
"Bu tabloda tüm modelleri karşılaştırabilirsiniz.

Accuracy'de BERT lider, hızda FastText lider, açıklanabilirlikte TF-IDF lider.

Her modelin farklı güçlü yanları var, bu yüzden hepsini birlikte kullanıyoruz."

## Slide 10: Web Log Analysis (40 saniye)
"Web log analizi için Isolation Forest algoritması kullanıyoruz.

Unsupervised learning - etiketli veri gerektirmiyor.

SQL injection, XSS, brute force, DDoS saldırılarını tespit edebiliyoruz.

Yüzde 92 üzeri accuracy ve sadece 15 milisaniye inference süresi var.

IP adresi, HTTP method, request path, user agent gibi özellikleri analiz ediyoruz."

## Slide 11: Correlation Engine (45 saniye)
"En önemli özelliklerimizden biri korelasyon motoru.

E-posta ve web tehditlerini birbirine bağlıyoruz.

Örneğin, aynı IP'den hem phishing e-postası hem de web saldırısı gelirse, risk 2 katına çıkıyor.

Unified risk formülümüz: Email risk çarpı 0.4, artı Web risk çarpı 0.4, artı Correlation çarpı 0.2.

Sonuç 0-100 arası unified risk skoru - LOW, MEDIUM, HIGH veya CRITICAL olarak sınıflandırılıyor."

## Slide 12: Explainable AI - LIME (35 saniye)
"Açıklanabilir AI çok önemli çünkü güvenlik analistleri modelin neden bu kararı verdiğini bilmek istiyor.

LIME ile her tahmin için hangi kelimelerin etkili olduğunu gösteriyoruz.

Örneğin 'urgent', 'verify', 'click here' kelimeleri pozitif katkı yapıyor - phishing göstergesi.

'Regards' kelimesi negatif katkı yapıyor - meşru e-posta göstergesi.

Bu şeffaflık, modele güveni artırıyor."

## Slide 13: Test Results (30 saniye)
"Test sonuçlarımız:

BERT ile yüzde 96.2 e-posta tespit accuracy'si.

Web anomali tespitinde yüzde 87.5 accuracy.

2 saniyenin altında yanıt süresi - SLA hedefimizi karşılıyoruz.

Yüzde 97.7 test pass rate.

31,000'den fazla etiketli e-posta ile eğitim yaptık."

---

# 👤 PRESENTER 3 (Slides 14-19) - Yaklaşık 3 dakika

## Slide 14: Dashboard Features (35 saniye)
"Web dashboard'umuzda altı ana özellik var:

E-posta analizi - içerik yapıştırıp anında sonuç alabilirsiniz.

Web log analizi - Apache, Nginx, IIS loglarını destekliyoruz.

Korelasyon görünümü - tehdit ilişkilerini görselleştiriyoruz.

İstatistikler - gerçek zamanlı grafikler ve alertler.

Model karşılaştırma ve raporlar.

Türkçe-İngilizce dil desteği ve dark mode da mevcut."

## Slide 15: Docker Infrastructure (30 saniye)
"Prodüksiyon ortamı için 9 Docker container kullanıyoruz:

Flask API, PostgreSQL veritabanı, Redis cache.

Nginx reverse proxy, Prometheus monitoring, Grafana dashboards.

Adminer veritabanı yönetimi, Portainer container yönetimi, Mailhog e-posta testi.

Tek komutla tüm sistem ayağa kalkıyor: docker-compose up -d."

## Slide 16: Standards and Compliance (30 saniye)
"Güvenlik standartlarına uyumluyuz:

ISO 27001, NIST Cybersecurity Framework, OWASP Top 10.

GDPR ve KVKK veri koruma gereksinimlerini karşılıyoruz.

Yazılım mühendisliğinde IEEE 29119 test standardı ve SOLID prensiplerini uyguladık.

SDG Goal 9 - Sanayi, Yenilik ve Altyapı hedefine katkı sağlıyoruz."

## Slide 17: Limitations and Future Work (30 saniye)
"Mevcut sınırlamalarımız:

Şu an sadece İngilizce e-posta modeli var - Türkçe planlıyoruz.

BERT GPU ile daha hızlı çalışır.

VirusTotal free tier rate limit'leri var.

Gelecekte network traffic analizi, Apache Kafka streaming ve SOAR entegrasyonu planlıyoruz."

## Slide 18: Conclusion (30 saniye)
"Sonuç olarak:

Yüzde 96.2 e-posta, yüzde 87.5 web tespit accuracy'si elde ettik.

2 saniyenin altında yanıt süresi sağladık.

LIME ile açıklanabilir AI entegre ettik.

Cross-vector korelasyon ile koordineli saldırıları tespit edebiliyoruz.

Bu proje, açıklanabilir ve entegre tehdit tespitinin hem mümkün hem de değerli olduğunu gösteriyor."

## Slide 19: Thank You (15 saniye)
"Sunumumuz burada sona eriyor. Sorularınız için hazırız. Teşekkür ederiz."

---

# ⏱️ ZAMAN ÖZETİ

| Presenter | Slides | Süre |
|-----------|--------|------|
| Presenter 1 | 1-7 | ~3.5 dk |
| Presenter 2 | 8-13 | ~3.5 dk |
| Presenter 3 | 14-19 | ~3 dk |
| **TOPLAM** | 19 slide | **~10 dk** |

---

# 💡 SUNUM İPUÇLARI

1. **Hız:** Normal konuşma hızında okuyun, acele etmeyin
2. **Geçişler:** Bir sonraki kişiye geçerken "Teşekkürler, şimdi [isim] devam edecek" diyebilirsiniz
3. **Demo:** Eğer zaman kalırsa localhost:5000 üzerinden canlı demo yapabilirsiniz
4. **Sorular:** "Bu konuda soru var mı?" diye ara soru almayın, sonunda toplu alın
5. **Teknik detay:** Hoca teknik detay sorarsa slide'lara referans verin

---

# 🎯 MUHTEMEL SORULAR VE CEVAPLAR

**S: Neden BERT'e en yüksek ağırlık?**
C: BERT en yüksek accuracy'yi sağlıyor ve bağlamı en iyi anlayan model.

**S: Gerçek zamanlı mı çalışıyor?**
C: Evet, 2 saniyenin altında yanıt süresi var.

**S: Türkçe destek var mı?**
C: Dashboard Türkçe, ama e-posta modeli şu an İngilizce. Türkçe model planlıyoruz.

**S: SHAP neden yok?**
C: SHAP denedik ama gerçek zamanlı kullanım için çok yavaştı, LIME daha hızlı.

**S: Ensemble neden bu ağırlıklar?**
C: F1-score bazlı optimizasyon yaptık, BERT en iyi performansı gösterdi.
