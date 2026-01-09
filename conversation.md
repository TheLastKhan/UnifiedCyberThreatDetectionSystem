Hocayla konuşma bölümü:

Hoca:
Arkadaşlar merhaba,
Genel hatlarıyla söz verdiğiniz süreci tamamladığınız bir vize dönemiydi. Gösterdikleriniz bence kıymetliydi. Üç kişi olduğunuz için görece yapılanlar az gibi algılandı ama sürecinizi açıkladım. Yine de Finale kadar çalışmanızın üzerine katmanız gereken bazı kısımlar olabilir.
Risk skor formülünü neye göre belirlediniz? Karşılaştığınız başka formüller var mı? Bunu başka bir literatürden mi temel aldınız?
Özellikle Security & UI ve Database kısmını (Roadmap and Future Work)’te bahsettiğiniz yaparsanız güzel olur.
Türkçe olması ihtimali var mı arayüzün?
TF-IDF ağırlıklandırma yöntemi konusunda biraz sınadı hocalar. Bu yönteme güveniyorsanız savunmanız lazım, güvenmiyorsanız bir ağırlıklandırma yöntemi daha kullanarak ikisi arasındaki karşılaştırmayı finalde sunmak güzel olur (Vizede şunu demiştiniz, o an emin olamadık, karşılaştırdık ve böyle bulduk gibi bir ifadeyle savunmanız hakim olduğunuzu gösterir.). fasttext gibi semantik bilgi taşıyan embeddingler kullanılabilir mi belki, bir bakabilirsiniz.
Onun haricinde, vize için benim görüşüme göre yeterli bir ilerlemeydi. Epey de iş yaptınız ama final için hocaların beklentileri biraz fazla, yukarıdaki maddeleri yerine getirip yaptıklarınızı sahiplenerek savunursanız, finali de sorunsuz atlatırsınız diye düşünüyorum.
Kolay gelsin

Ben:
Öncelikle olumlu yorumlarınız ve süreci açıkladığınız için çok teşekkür ederiz hocam... Evet finalde aklımızda eklemeyi düşündüğümüz yerler var. Elimizden geldiğince hepsini yapmaya çalışacağız. Önceliğimiz Roadmap ve Future Work'te bahsedildiği gibi stateful olması, docker container eklemek, kaggle'dan aldığımız gerçek veriler ile çalışmak, database kısmına entegre etmek ve virustotal api ile entegrasyonu sağlayabilmek. Ve zamanımız kalırsa da daha da ekleyebileceğimiz bir şeyler olursa onları eklemeye çalışıp projeyi büyütebilmek.
 
Hocam, risk skor formülümüz bu şekilde: min(100, (EmailRisk * 0.4) + (WebRisk * 0.4) + CorrelationBonus). Heuristic Weighted Scoring diye geçiyor. Araştırmalarımıza göre SIEM sistemlerinde farklı kaynaklardan gelen alarmları normalize etmek için genelde bu tür ağırlıklı ortalamalar standart olarak kullanılıyormuş. E-posta ve web saldırıları eşit derece önemli kabul edildiği için %40 pay verdik. Geriye kalan %20 ise korelasyon durumuna göre ayırdık (Multi-vector threat olarak). Eğer bir tehlike kaynağı daha eklemek durumunda olsaydık hepsine %30 pay verip korelasyona %10 verebilirdik. Daha dengeli olması açısından bu şekilde düşündük.
 
TF-IDF seçme sebebimiz aslında hızlı olması ve LIME ile uyumlu olmasıydı. O şekilde daha kolay bir şekilde hangi kelimenin ne kadar puan getirdiğini görebiliyorduk. Ama elbette eski olması biraz sorun yaratabilir. Onun için daha yeni bir model eğitebiliriz. Aklımızda word embeddings kullanan fasttext veya BERT (DistilBERT) var. Sonra sizin de dediğiniz gibi TF-IDF ve fasttext / BERT karşılaştırması tablosu koyabiliriz.
 
UI Türkçe elbette olabilir hocam. Komple mi Türkçe olması daha iyi olur, yoksa hem türkçe hem de ingilizce versiyonları olacak şekilde mi olması daha uygun olur?
 
Aklıma gelen konular şimdilik bunlar hocam. Sunum hakkındaki geri dönüşünüz için tekrardan teşekkürler. Ve ayrıca geçmiş olsun hocam. Umuyoruz ki ciddi bir durumunuz yoktur.
 
İyi akşamlar dilerim hocam.

Hoca:
Teşekkür ederim Nurettin. Türkçe ve İngilizce ikisi de olabiliyorsa daha güzel tabii. Karşılaştırma tablosu da güzel olur, genelde konuya hakimiyet göstergesi olarak algılanıyor karşılaştırmalar. Future work'teki kısımları yapacaksanız beklentiyi fazlasıyla karşılamış olursunuz. Elinize sağlık. İyi akşamlar

Ben:
Rica ederiz Hocam. Türkçe-İngilizce UI ve karşılaştırma tablosu da eklemeye çalışacağız hocam. Ve ayrıca diğerlerini de aynı şekilde. Tekrardan teşekkür ederiz, iyi akşamlar hocam.
Gamze Hocam merhabalar. daha önce bir proje tanıtım raporu size göndermek istiyorduk ancak sınavlara hazırlık ve başka derslerin de proje ödevlerinden doğan yoğunluktan dolayı size ancak şimdi raporu hazırlayabildik. 
 
içime sinmeyen yerler var hala raporda da projede de ancak bir fikir oluşması açısından yine de bu raporu ekran görüntüleri ile sizle paylaşmak istedik. hangi sayfada neler yapılıyor, kullanılan teknolojiler neler, modellerin kıyaslamaları, raporlamalar ve ayarlar gibi içerikler mevcut. 
 
hocam kusura bakmayın lütfen, haftasonu anca hazırlayabildik. haftaiçi de projenin hatalarını düzeltmeye çalıştık. her şey üstüste geldi, yoğunluktan dolayı bu şekilde bir şey yapabildik. yani siz müsait olunca inceleyebilirseniz sonraki haftaiçi sizin için de daha uygun olur diye düşünüyoruz.  
 
yardımlarınız ve geri dönütleriniz için çok teşekkürler hocam, iyi günler ve iyi haftasonları dileriz.
Hocam bunlar da sayfalardaki bölümlerin işlevlerini gösteren kısa videolar. direkt bu dosyaları browser ile açabilirsiniz. 
tekrardan teşekkürler, iyi günler hocam.
Çok teşekkürler hocam. bu arada bazı ekran görüntüleri ve videolar biraz eksik ve kesilmiş gibi olmuş hocam, tam ekran görüntülerini de şimdi gönderiyorum. tekrardan iyi günler dilerim hocam.

Hoca:
Tekrar merhaba arkadaşlar, 
 
Gayet güzel bir proje çıkardınız, elinize sağlık. Sizin içinize sinmeyen konular neydi? 
 
Özellikle raporunuzda yazarken dikkat etmeniz gereken bazı noktalar var:
 
Software architecture'ınız var ama yüzeysel, burada mimari karakterini tanımlamanız güzel olur. Örneğin distributed ya da event-driven, log-driven system gibi bir tanımlama gerekiyor. 
Katmanları sorumluluklarıyla ayırmanız güzel olur. Şuan Flask Rest API, Docker ve BERT /FastText'ten bahsediyorsunuz ancak mimari anlatı çok sınırlı kalıyor. Burada yazılım mimari tasarımının rasyonelize edildiği arka plan için, şunları söylemeniz güzel olur:
Sistem event-driven mı yoksa request-response mu?
Phishing + Web log neden aynı backendde?
Model inference neden API içinde?
Şöyle bir açıklama da güzel olur: CyberGuard is designed as a modular, service-oriented architecture where the sensing logic and presentation layers are separated which allows machine learning models to develop independently.
 
Sizde microservice benzeri yapı, cache-aside, ensemble model yaklaşımı gibi tanımlar var ama burada biraz daha eşleştirme güzel olur. Bir tablo hazırlayabilir misiniz? Bir sütununda Pattern, diğer sütununda CyberGuard'da karşılığı gibi bir eşleştirme olabilir (Pattern-Mapping). Böylece kullandığınız yazılım mimarisi ve tasarım kalıplarını tesadüf olarak değil de bilinçli olarak seçtiğinizi ve sistemin parçalarına uygulandığını ifade etmiş olursunuz. 
Model-View-Controller (MVC) -> Dashboard (View), Flash API (Controller), PostgreSQL ve ML Models (Model)
Event-Driven/Publisher-Subscriber, Email/Web log ingestion -> detection -> correlation
Ensemble Learning, BERT, FastText ve TF-IDF sonuçlarınını birlikte değerlendirilmesi
Cashe-Aside Pattern, Redis ile sık erişilen istatistiklerin cachelenmesi 
 
Böyle bir eşleştirme tablosu kurduktan sonra açıklamanız da önemli: CyberGuard sistemi, bilinen birçok mimari ve tasarım modelini örtük olarak benimser. Sistem açıkça tek bir model etrafında tasarlanmamış olsa da, modüler yapısı doğal olarak MVC ve olay odaklı prensiplerle uyumludur. Bu yaklaşım, sistemin bakım kolaylığını, ölçeklenebilirliğini ve genişletilebilirliğini artırır.
 
Bu kısım biraz daha sizin software engineering dersinde öğrendiğiniz kavramları ölçmeye çalıştığı için halihazırda dersi alırken nereleri ekleyebileceğinizi tekrar değerlendirin isterseniz. 
 
Test design'da mutlaka testin amacını yazmalısınız. Şu an test listesi ve performans rakamı var ancak test methodology başlığı ekleyerek, neden accuracy ölçüldü? neden latency ölçülmedi? load test neden yok? gibi sorulara cevap vermeniz güzel olur. 
 
Sonuçların karşılaştırılması kısmında da raporunuza yazarken mutlaka ve mutlaka yanlış pozitiflerden bahsetmeniz, model trade-offlarını raporlamanız ve gerçek dünya risklerinden bahsetmeniz güzel olur. Birkaç başlık ekleyebilirsiniz burada: Neden BERT diğerlerinden daha iyi performans gösterdi? Hız vs Doğruluk trade-off ya da concept drift risk gibi. 
 
Şu haliyle daha çok mevcut ürününüzün dökümü için bir belge hazırladığınız için bu ayrıntıların olmaması çok normal. Raporunuzu yazarken dikkat edebilirseniz güzel olur. Onun haricinde sizin söylemek istediğiniz bir şey olursa hafta içinde tekrar iletişime geçebiliriz. 
 
Elinize sağlık tekrar, sınavlarınızda başarılar dilerim

Ben:
Merhaba, iyi akşamlar hocam, teşekkür ederiz.
 
İçimize sinmeyen birkaç konu vardı:
 
1- Virustotal api entegrasyonu (request sıklığına göre) virustotalden dolayı bazen çalışıyor, bazen çalışmıyor. yani entegre etmek istiyoruz, projeden de çıkarmak istemiyoruz ancak bazen böyle istediğimiz sonuçları veremeyebiliyor.
 
2- Fasttext normalizasyon sorunu. Yani normalizasyon yapılmazsa istenilen sonucu veremeyebiliyor. mantıksız oluyor. çok defa farklı kaynaklar ile colab'da eğitmeyi denedik ancak bert ve tf-idf gibi beklediğimiz gibi çalışmayabiliyor. o yüzden mantıklı sonuç gösterebilmesi için mecburi bir şekilde birkaç düzenleme yapmak durumunda kaldık.
 
3- Hybrid-Ensemble halini dashboardda gösterip göstermeme konusunda karar veremedik. Şu an dashboardda görsel olarak tf-idf verileri kullanılıyor. yani e-mail phishing bölümünde 3 model de çalışıyor ve database'e kaydediliyor. redis cache olarak da kullanılıyor. sadece hybrid api olarak (bert * 0.5 + fasttext * 0.3 + tf-idf * 0.2) önem ağırlığına göre dashboardda gösterip göstermeyelim mi onu düşündük. zaman kalırsa onun hakkında tekrar düşüneceğiz.
 
Haklısınız hocam biraz yüzeysel oldu bu rapor. Aslında asıl vereceğimiz final raporuna göre bir ön-rapor gibi oluşturmak istemiştik. ön bilgilendirme raporu gibi. Sizin belirttiğiniz yerleri de ekleyip güncelleyerek raporu tekrardan biraz daha düzenledik.
 
Geri bildiriminiz için tekrardan teşekkürler, tekrardan iyi akşamlar dilerim hocam.

Hoca:
Elinize sağlık, aslında bu dediklerinizi raporunuzda net bir şekilde ifade edebilirseniz çok sorun değil. Api entegrasyonunu rate limitlere göre senaryolar belirleyip başarılı ve başarısız durumları yazmak güzel olabilir. Fasttextte de neden normalizasyon gerektigi ve yine farklı senaryolar üzerinden model karsilastirmalarini yazmanız değerli olur. Eğer son kararı hybrid vermeyi planladiysaniz bu ağırlığı kullanabilirsiniz ama aksi halde karşılaştırmalara göre en iyi sonuç verenin dashboardda gösterildiğini, diğer ikisinin model karsilastirmasi yapabilmek adına backend de tutulduğunu söylemek güzel olur. Eğer senaryolara göre daha iyi sonuç veren bir model varsa, duruma göre en iyi sonucu vereni kullanacak şekilde dashboard da göstermek güzel olabilir, bu da ayrıca söylenebilir (biz bu şekilde yaptık ama tf idf verileri kullanılıyor şuana kadarki senaryolardan gibi) 
 
Bence gayet güzel, elinize sağlık, eksik olarak gördüğünüz kısımları açıkladığıniz ve farklı senaryolarla test edip karsilastirmalarini raporladiginiz sürece sorun olacağını sanmıyorum 
Bu turkce versiyon projenize ek bir materyal olarak da çok değerli olmuş ancak proje raporunuzu, eski format üzerinden eksik kalan kısımları doldurarak yazacaksınız değil mi? Yanlış anlamamak adına sormak istedim 

" gibi bir şey işte... teamsteki konuşmalar bunlar hemen hemen vizeden sonra... en azından elimizde eli yüzü düzgün bir rapor olsun da... ondan şimdiden yazıyorum sana bunu... bugün projede düzeltmeyi deneyeceğim yerler var da... eğer bir şey değişirse onları da değiştirip proje raporunu tekrar güncelleriz diyordum...

nasıl fikir sence? sana uygun mu? teşekkürler şimdiden...