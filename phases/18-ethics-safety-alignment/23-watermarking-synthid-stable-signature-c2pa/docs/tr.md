# Filigranleme — SynthID, Stable Signature, C2PA

> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/18-ethics-safety-alignment/23-watermarking-synthid-stable-signature-c2pa/docs/en.md)

> Üç teknoloji 2026 AI-üretilmiş-içerik kökenini yapılandırır. SynthID (Google DeepMind) — Ağustos 2023'te başlatılan görüntü filigranleme, Mayıs 2024'te metin+video (Gemini + Veo), Ekim 2024'te Responsible GenAI Toolkit yoluyla metin açık kaynak, Kasım 2025'te Gemini 3 Pro ile birlikte birleşik çoklu-ortam detektörü. Metin filigranleme, sonraki-token örnekleme olasılıklarını fark edilemeyecek şekilde ayarlar; görüntü/video filigranları sıkıştırmaya, kırpmaya, filtrelere, kare hızı değişikliklerine dayanır. Stable Signature (Fernandez ve ark., ICCV 2023, arXiv:2303.15435) — gizli difüzyon kod çözücüsünü, her çıktının sabit bir mesaj içermesi için ince ayar yapar; kırpılmış (içeriğin %10'u) üretilmiş görüntüler FPR<1e-6'da >%90 tespit edilir. Devamı "Stable Signature is Unstable" (arXiv:2405.07145, Mayıs 2024) — ince ayar, kaliteyi korurken filigranı kaldırır. C2PA — kriptografik olarak imzalanmış, kurcalamaya-karşı-dayanıklı (tamper-evident) metadata standardı (C2PA 2.2 Explainer 2025). Filigranleme ve C2PA tamamlayıcıdır: metadata sıyrılabilir ancak daha zengin köken taşır; filigranlar kod dönüştürme boyunca kalır ancak daha az bilgi taşır.

**Tür:** Uygulama
**Diller:** Python (stdlib, token-filigran gömme + tespit)
**Ön Koşullar:** Faz 10 · 04 (örnekleme), Faz 01 · 09 (bilgi teorisi)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Token-düzeyinde filigranlemeyi (SynthID-metin tarzı) ve tespit edilebilirlik mekanizmasını açıklayın.
- Stable Signature'ı ve onu kıran 2024 kaldırma saldırısını açıklayın.
- C2PA'nın rolünü ve filigranlemeyi neden tamamladığını belirtin.
- Anahtar sınırlamaları açıklayın: modele-özgü sinyal, özet çıkarma (paraphrase) altında sağlamlık ve anlam-koruyan saldırılar (arXiv:2508.20228).

## Sorun

2023-2024'te deepfake'ler ve AI-üretilmiş içerik siyasi ve tüketici bağlamlarında ölçekli olarak ortaya çıktı. Filigranleme, önerilen teknik köken sinyalidir: oluşturma zamanında nesilleri işaretleyin, sonra tespit edin. 2025 kanıtı: hiçbir filigran koşulsuz olarak sağlam değildir, ancak C2PA metadata ile katmanlandığında kombinasyon kullanılabilir bir köken hikayesi sağlar.

## Kavram

### Metin filigranleme (SynthID-metin tarzı)

Kirchenbauer ve ark. 2023 mekanizması, Google tarafından üretimleştirildi:

1. Her kod çözme adımında, önceki K token'ı, kelime hazinesinin "yeşil" ve "kırmızı" kümelerine yalancı rastgele bir bölümleme üretmek için hashleyin.
2. Yeşil logitlerine δ ekleyerek örneklemeyi yeşil kümeye doğru yönlendirin.
3. Nesil, şansın üreteceğinden daha fazla yeşil token içerir.

Tespit: her öneki yeniden hashleyin, nesildeki yeşil tokenları sayın, bir z-skoru hesaplayın. z-skoru filigranlı metin için >0, insan metni için ~0'dır.

Özellikler:
- Okuyucular için fark edilemez (δ kalite kaybının küçük olduğu kadar küçüktür).
- Kelime hazinesi bölümleme fonksiyonuna erişimle tespit edilebilir.
- Özet çıkarmaya (paraphrase) karşı sağlam değil — metni yeniden yazmak sinyali yok eder.

SynthID-metin, Ekim 2024'te Google'ın Responsible GenAI Toolkit yoluyla açık kaynak yapıldı.

### Stable Signature (görüntü)

Fernandez ve ark. ICCV 2023. Gizli difüzyon kod çözücüsünü, her üretilmiş görüntünün gizli temsiline gömülü sabit bir ikili mesaj içermesi için ince ayar yapar. Tespit, gizli temsilden sinirsel bir kod çözücü ile kod çözülür. İçeriğin %10'una kırpılmış görüntüler FPR<1e-6'da >%90 tespit edilir.

Mayıs 2024 "Stable Signature is Unstable" (arXiv:2405.07145): kod çözücüyü ince ayar yapmak, görüntü kalitesini korurken filigranı kaldırır. Düşmanca üretim-sonrası ince ayar ucuzdur; filigranın düşmanca sağlamlığı sınırlıdır.

### SynthID birleşik detektörü (Kasım 2025)

Gemini 3 Pro ile birlikte: bir API'de metin, görüntü, ses ve video'dan SynthID sinyallerini okuyan çoklu-ortam detektörü. Google köken yığınını birleştirir.

### C2PA

İçerik Kökeni ve Otantikliği Koalisyonu (Coalition for Content Provenance and Authenticity). Kriptografik olarak imzalanmış kurcalamaya-karşı-dayanıklı metadata standardı. C2PA 2.2 Explainer (2025). Bir C2PA manifesti, oluşturucunun anahtarıyla imzalanmış köken iddialarını (kim oluşturdu, ne zaman, hangi dönüşümler) kaydeder.

Filigranlemeyi tamamlayıcı:
- Metadata sıyrılabilir; filigranlar (kolayca) sıyrılamaz.
- Metadata zengindir (tam köken zinciri); filigranlar bit taşır.
- C2PA platform benimsenmesine bağlıdır; filigranlar otomatik olarak gömülür.

Google, Search, Ads ve "Bu görüntü hakkında"da ikisini de entegre eder.

### Sınırlamalar

- **Modele özgü.** SynthID, SynthID-etkin modellerden gelen nesilleri filigranlar. SynthID olmadan bir modelden gelen nesil filigranlanmaz, dolayısıyla "SynthID sinyali yok" otantikliğin kanıtı değildir.
- **Özet çıkarma (Paraphrase).** Metin filigranları anlam-koruyan özet çıkarmadan sağ çıkmaz.
- **Dönüşüm saldırıları.** arXiv:2508.20228 (2025) hem metin filigranlarını hem de birçok görüntü filigranını yok eden anlam-koruyan saldırılar gösterir.
- **İnce-ayar-kaldırma.** "Stable Signature is Unstable"a göre, üretim-sonrası ince ayar gömülü filigranları kaldırır.

### AB AI Yasası Madde 50

AI-üretilmiş içerik etiketleme için Şeffaflık Kodu (ilk taslak Aralık 2025, ikinci taslak Mart 2026, [Avrupa Komisyonu durum sayfasına](https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content) göre Haziran 2026'da beklenen son). Kod, Nisan 2026 itibarıyla taslak halindedir ve zaman çizelgesi değişikliğe tabidir. Teknik katmanı gerektiren düzenleyici katman. Deepfake'ler etiketlenmelidir.

### Bu, Faz 18'de nereye oturuyor

Dersler 22-23, modelin ne yaptığı (özel veri, köken sinyali) hakkındadır. Ders 27, eğitim-veri yönetişimini kapsar. Ders 24, bu teknik önlemleri gerektiren düzenleyici çerçevedir.

## Uygulama

`code/main.py` bir oyuncak metin filigranı inşa eder. Tokenlar 0..N-1 tamsayılarıdır; filigranlı örnekleme, hash-tarafından-tanımlanmış yeşil kümeye doğru yönlendirir. Bir detektör yeşil-token z-skorunu hesaplar. 1000 tokenlık nesillerde tespiti gözlemleyebilir, özet çıkarmanın sinyali yok ettiğini izleyebilir ve insan metnindeki yanlış-pozitif oranını ölçebilirsiniz.

## Ship It

Bu ders `outputs/skill-provenance-audit.md` üretir. Bir köken iddiası olan içerik dağıtımı verildiğinde, filigran mekanizmasını (varsa), C2PA imzalama zincirini (varsa), her birinin düşmanca sağlamlığını ve modalite başına kapsamı denetler.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. 1000 tokenlık filigranlı nesil vs insan-yazılı metin için z-skorlarını raporlayın. %95 güven eşiğinde yanlış-pozitif oranını tanımlayın.

2. Tokenların %30'unu eş anlamlılarla değiştiren bir özet-çıkarma saldırısı uygulayın. z-skorunu yeniden ölçün.

3. Kirchenbauer ve ark. 2023 Bölüm 6'yı sağlamlık üzerine okuyun. Metin filigranları özet çıkarma altında neden başarısız olur ama görüntü filigranları kırpma altında neden sağ kalır?

4. SynthID-metin + C2PA metadata kullanan bir dağıtım tasarlayın. Bir tüketicinin gördüğü köken zincirini açıklayın. Her bileşenin bir başarısızlık modunu tanımlayın.

5. 2024 "Stable Signature is Unstable" sonucu, ince ayarın görüntü filigranını kaldırdığını gösterir. Bu saldırıyı sınırlayan bir dağıtım kontrolü tasarlayın — örneğin, ince-ayar yapılmış kontrol noktalarının imzalı sürümlerini gerektirin.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|---------------------|---------------|
| SynthID | "Google'ın filigranı" | Çapraz-modal köken sinyali; metin, görüntü, ses, video |
| Token filigranı | "Kirchenbauer tarzı" | Yeşil-token z-skoru yoluyla tespit edilebilir yönlendirilmiş-örnekleme metin filigranı |
| Stable Signature | "görüntü filigranı" | İnce-ayarlı-kod-çözücü filigranı; ICCV 2023 |
| C2PA | "metadata standardı" | Kriptografik olarak imzalanmış kurcalamaya-karşı-dayanıklı köken metadatası |
| Özet çıkarma sağlamlığı | "yeniden ifade etmek onu kırar mı" | Metin filigranı özelliği; şu anda sınırlı |
| İnce-ayar kaldırma | "düşmanca filigran kaldırma" | Kod çözücü ince ayarı yoluyla görüntü filigranını kaldıran saldırı |
| Çapraz-modal detektör | "birleşik SynthID" | Kasım 2025 modeller arası birleşik API |

## İleri Okuma

- [Kirchenbauer ve ark. — A Watermark for Large Language Models (ICML 2023, arXiv:2301.10226)](https://arxiv.org/abs/2301.10226) — token-filigranı mekanizması
- [Fernandez ve ark. — Stable Signature (ICCV 2023, arXiv:2303.15435)](https://arxiv.org/abs/2303.15435) — görüntü filigranı makalesi
- ["Stable Signature is Unstable" (arXiv:2405.07145)](https://arxiv.org/abs/2405.07145) — kaldırma saldırısı
- [Google DeepMind — SynthID](https://deepmind.google/models/synthid/) — çapraz-modal filigran
- [C2PA 2.2 Explainer (2025)](https://c2pa.org/specifications/specifications/2.2/explainer/Explainer.html) — metadata standardı
