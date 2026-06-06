# LLaVA-OneVision: Tek Görüntü, Çoklu Görüntü, Tek Modelde Video

> LLaVA-OneVision'dan (Li ve diğerleri, Ağustos 2024) önce açık-VLM dünyasında ayrı soylar vardı: tek görüntüler için LLaVA-1.5, Mantis ve VILA gibi çoklu görüntü modelleri, Video-LLaVA ve Video-LLaMA gibi video modelleri. Her biri kendi kıyaslama testini kazandı ve diğerlerinde başarısız oldu. LLaVA-OneVision, tek bir müfredatın (curriculum) tek bir modeli üç senaryonun hepsinde baskın hale getirecek şekilde eğitebileceğini ve ortaya çıkan görev aktarımı etkilerinin (tek görüntü becerilerinin videoya aktarılması, çoklu görüntü akıl yürütmesinin tek görüntüye aktarılması) uzmanların toplamını yendiğini savundu. Tarif aldatıcı kadar basittir: senaryolar boyunca sabit kalan bir görsel-token bütçesi, ardından tek görüntüden OneVision'a (çoklu görüntü), oradan videoya geçen açık bir müfredat. Bu ders bütçeyi, müfredatı ve ortaya çıkan davranışları inceler.

**Tür:** İnşa Et
**Diller:** Python (stdlib, token bütçesi çözücü + müfredat planlayıcı)
**Önkoşullar:** Faz 12 · 05 (LLaVA), Faz 12 · 06 (her çözünürlük)
**Süre:** ~180 dakika

## Öğrenme Hedefleri

- Tek görüntü, çoklu görüntü ve video girdileri arasında sabit kalan bir görsel-token bütçesi tasarlama.
- Tek görüntüden videoya becerileri felaket unutma olmadan aktaran bir eğitim müfredatı sıralama.
- Doğru müfredatla tek bir modelin aynı parametre sayısında neden uzmanları yendiğini açıklama.
- LLaVA-OneVision tarafından bildirilen üç ortaya çıkan yeteneği adlandırma: çoklu kamera akıl yürütmesi, işaret kümesi (set-of-mark) istemleme, iPhone ekran görüntüsü ajanı.

## Sorun

Görüntü, çoklu görüntü ve video her birini farklı strese sokar.

Tek görüntü, OCR ve ince ayrıntıları yakalamak için yüksek çözünürlüklü token'lar ister (AnyRes, ~2880 görsel token). Örnek başına bütçe: bir görüntü, 2880 token.

Çoklu görüntü, akıl yürütmesinin bağlama sığması için orta çözünürlükte birkaç görüntü ister (~576 token her biri). Örnek başına bütçe: 4-8 görüntü, her biri 576, 2300-4600 token.

Video, zamansal dinamikleri yakalamak için çözünürlük havuzlamasından sonra birçok kare ister (~196 token kare başına). Örnek başına bütçe: 8-32 kare, her biri 196, 1600-6200 token.

Ayrı modeller eğitirseniz bir bütçe seçersiniz. Tek model eğitirseniz bütçenin bağlamı patlatmadan senaryolar arasında makul bir şekilde ölçeklenmesi gerekir.

OneVision öncesi varsayılan cevap "tek bir senaryoyu eğitin, diğerlerini görmezden gelin" idi. Video-LLaVA, fazladan eğitim aşamalarıyla bir görüntü modeline videoyu ekledi. LLaVA-NeXT döşeme ile çoklu görüntü desteği ekledi. Hiçbiri üçünü birden temiz işleyemedi.

## Kavram

### OneVision token bütçesi

LLaVA-OneVision, örnekte yaklaşık 3000-4000 token olan tek bir görsel-token bütçesi seçer, her senaryoya farklı şekilde dağıtır:

- Tek görüntü: AnyRes-9 (3x3 döşeme + küçük resim), her döşeme 384'te 729 yama, agresif çift doğrusal havuzlama 2x2 → döşeme başına 182. Toplam: 9 * 182 + 182 = 1824 token. Veya döşeme başına 729 ile AnyRes-4 = 2916 + 729.
- Çoklu görüntü: her görüntü orta çözünürlükte (384, döşeme yok), havuzlama yok 729 token. Bütçe 6 görüntü → 4374 token.
- Video: 384 çözünürlükte 32 kare, agresif 3x3 çift doğrusal havuzlama → kare başına 81 token. Toplam: 32 * 81 = 2592 token.

Dağılım yaklaşık sabit toplam token korur. LLM asla bağlamını patlatan bir toplu iş görmez. Kodlayıcı her senaryo için farklı geometri üretir ama LLM aynı bütçeyi tüketir.

### Üç aşamalı müfredat

LLaVA-OneVision üç aşamada eğitilir:

1. Tek görüntü SFT (SI aşaması). Tüm veri tek-görüntü-artı-metindir. Yüksek çözünürlüklü AnyRes girdisi üzerinde eğitilir. Bu algılamayı, OCR'yi ve ince düzeyde anlama becerisini öğretir. LLaVA-NeXT verileri artı OneVision'a özgü tek görüntü verileri kullanılır.
2. OneVision SFT (OV aşaması). Tek görüntü + çoklu görüntü + video (eşit örneklenmiş kareler) karıştırılır. Birleşik token bütçesi üzerinde eğitilir. Bu modelin heterojen toplu iş şekillerini nasıl işleyeceğini öğretir. Ağırlık sıfırlaması yok — SI aşamasından devam eder.
3. Görev aktarımı (TT aşaması). Hedef görev karışımıyla devam edilir, genellikle ürüne bağlı olarak daha ağır çoklu görüntü veya video. Dağıtım için isteğe bağlı ince ayar.

Kritik: müfredat sırası önemlidir. Videoyu veya çoklu görüntüyü önce eğitmek, aynı verilerle olsa bile görüntü performansını tek görüntüden önce eğitmekten daha kötü üretir. Makale bunu açıkça kıyaslama deneyi olarak sunar.

### Neden müfredat işe yarar

Tek görüntü eğitimi temel algılamayı oluşturur. Yama token'ları ince düzeyde görsel özellikler taşır; LLM bunları metinle bütünleştirmeyi öğrenir. Çoklu görüntü ve video, güçlü bir algılam temeli olmadan öğrenmesi zor yapısal zorluklar (hangi görüntü hangisi, önce ne oldu) tanıtır.

Tüm senaryoları sıfırdan birlikte eğitirseniz model algılamayı yetersiz öğrenir (toplu iş başına sınırlı tek görüntü verisi) ve yapıya aşırı uyum sağlar (çoklu görüntü / video verisi bol). Sonuç: çapraz görüntü akıl yürütme kalıplarını takip eden ama görsel olarak sığ bir model.

Müfredat sıralaması size SI aşamasından algılama gücü, ardından OV aşamasından bileşimsel/zamansal akıl yürütmesi sağlar, ikisini de kaybetmeden.

### Ortaya çıkan çapraz-senaryo becerileri

LLaVA-OneVision makalesi üç ortaya çıkan yetenek bildiriyor:

1. Çoklu kamera akıl yürütmesi. Çoklu görüntü + video ayrı ayrı eğitildi; çıkarım sırasında çoklu kamera sürüş sahnesi hakkında akıl yürütmesi istendi. Model, tam olarak eğitimin o biçimini hiç görmemesine rağmen bakış açılarını doğru bir şekilde bütünleştirdi.
2. İşaret kümesi istemleme. Kullanıcı bir görüntüdeki nesneleri numaralı işaretlerle etiketler; model "işaret 3 işaret 7'ye göre ne yapıyor" diye akıl yürütür. Ne işaretler ne de etiketleme üzerinde eğitilmemiştir; uzamsal sapma + çoklu görüntü referansının birleşiminden öğrenilmiştir.
3. iPhone ekran görüntüsü ajanı. Kullanıcı bir iPhone ekranının ekran görüntüsünü verir ve bir sonraki tıklamayı planlamasını ister. Arayüz ekran görüntüleri, kullanıcı iş akışı videoları ve çoklu görüntü öncesi/sonrası çiftleri üzerinde eğitilir. Ajan kullanım durumuna genelleştirir.

Bunlar eğitilmiş görevler değil; müfredatın bileşimsel yapısından ortaya çıkarlar.

### Görsel-token havuzlaması

Token bütçesi havuzlama gerektirir. OneVision, 2D yama ızgarası üzerinde çift doğrusal enterpolasyon kullanır: 24x24 = 576 yama, 12x12 = 144'e (2x çarpanı) veya 8x8 = 64'e (3x çarpanı) dönüşür. Havuzlama yerelliği korumak için yama ızgarası uzayında, token uzayında yapılır.

Her senaryo için havuzlama çarpanı seçimi kendi başına bir hiperparametredir. Daha az havuzlama = daha fazla token = daha zengin temsil. Daha fazla havuzlama = daha az token = daha fazla kare / görüntü sığar.

### LLaVA-OneVision-1.5

2025 devamı (LLaVA-OneVision-1.5, arXiv 2509.23661) eğitim verilerinde, model ağırlıklarında ve kodda "tamamen açıktır". Bazı kıyaslama testlerinde tescelli farkla eşleşir ve tarifi demokratikleştirir. Aynı müfredat, daha fazla veri, daha iyi temel LLM. Mimari değişiklik yok.

### Qwen2.5-VL ile karşılaştırma

Qwen2.5-VL (Ders 12.09) farklı seçimler yapar. Sabit havuzlama yerine M-RoPE ve dinamik FPS kullanır. Bütçesi girdiyle ölçeklenir — 1 dakikalık video 5 saniyelik videodan fazla token kullanır. LLaVA-OneVision bütçeyi sabit tutar ve havuzlamayı ölçeklendirir. Her ikisi de çalışır; yapılandırılabilirlik ile öngörülebilirlik arasında takas yapar.

## Kullan

`code/main.py` bir OneVision tarzı VLM için müfredat ve bütçe planlayıcısıdır. Örnek başına token bütçesi ve hedef senaryo karışımı (ör. %40 tek görüntü, %30 çoklu görüntü, %30 video) verildiğinde:

- Her senaryo için çözünürlük, havuzlama çarpanı ve kare sayısını dağıtır.
- Her senaryonun paylaşılan bütçe dahilinde kalıp kalmadığını kontrol eder.
- Beklenen token sayısını, LLM FLOPs'larını ve hangi senaryoların token-yetersiz olduğunu raporlar.
- Aşama bazında eğitim takvimi yazdırır.

Bir OneVision ince ayarını planlamak veya bir VLM dağıtımının istek başına maliyetini doğrulamak için kullanın.

## Teslimat

Bu ders `outputs/skill-onevision-budget-planner.md` dosyasını üretir. Hedef görev dağılımı ve örnek başına bütçe verildiğinde, AnyRes çarpanını, kare başına havuzlamayı, video kare sayısını ve müfredat aşama ağırlıklarını üretir. Birleşik senaryo VLM'i her eğittiğinizde veya ince ayar yaptığınızda bunu kullanın.

## Alıştırmalar

1. Ürününüz %80 tek görüntü, %10 çoklu görüntü (2-4 görüntü), %10 video (8-16 kare) destekliyor. Token bütçesini tasarlayın. Ağır çoklu görüntü yapmayarak tasarruf ettiğiniz ek bütçeyi nereye koyardınız?

2. LLaVA-OneVision Bölüm 4.3'ü okuyun (ortaya çıkan yetenekler). Müfredatın büyük olasılıkla kilidini açacağı ama makalenin bildirmediği dördüncü bir ortaya çıkan beceri önerin.

3. Müfredat sırasını değiştirin — çoklu görüntüyü önce, tek görüntüyü sonra, videoyu en son eğitin. Hangi kıyaslama testlerinin bozulduğunu ve nedenini tahmin edin.

4. Makale, video kıyaslama testlerinin yalnızca örnek başına 8 kare ile eğitildiğini bildiriyor. Bu, çıkarım sırasında 30 saniyelik videolara genelleştirilir mi? İlk olarak ne kırılır — token bütçesi mi yoksa zamansal akıl yürütme mi?

5. 24x24 yamanın 12x12'ye çift doğrusal havuzlaması boyut başına 4x azaltmadır. Havuzlamayı stdlib Python'da uygulayın ve her 2x2 bloğun ortalamasının çift doğrusal çıktıyla eşleştiğini doğrulayın.

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| OneVision senaryosu | "Tek görüntü, çoklu görüntü veya video" | Birleşik VLM'in işlediği üç girdi şeklinden biri; bütçe tümü arasında sabit kalır |
| Token bütçesi | "Örnek başına kaç token" | LLM'in her eğitim / çıkarım örneğinde gördüğü toplam görsel token, genellikle 3000-4000 |
| Müfredat | "Eğitim sırası" | Ortaya çıkan aktarım için seçilen aşama sıralaması (tek görüntü → çoklu görüntü → video) |
| Çift doğrusal havuzlama | "Token küçültme" | Yama ızgarasına (2B) çift doğrusal enterpolasyon uygulayarak token sayısını yerelliği koruyarak azaltma |
| Ortaya çıkan beceri | "Eğitilmedi, hâlâ çalışıyor" | Eşleşen eğitim verisi olmadan ortaya çıkan çıkarım yeteneği, müfredat bileşimi nedeniyle |
| AnyRes-k | "k-döşeme kurulumu" | Sabit çözünürlükte k alt döşeme artı bir küçük resim, tipik k ∈ {4, 9} |
| Görev aktarımı | "Çapraz-senaryo genelleştirmesi" | Tek görüntüde öğrenilen ve paylaşılan omurga aracılığıyla videoya uygulanan beceriler (ve tersi) |

## İleri Okuma

- [Li ve diğerleri — LLaVA-OneVision (arXiv:2408.03326)](https://arxiv.org/abs/2408.03326)
- [LLaVA-OneVision-1.5: Tamamen Açık Çerçeve (arXiv:2509.23661)](https://arxiv.org/abs/2509.23661)
- [Lin ve diğerleri — Video-LLaVA (arXiv:2311.10122)](https://arxiv.org/abs/2311.10122)
- [Lin ve diğerleri — VILA (arXiv:2312.07533)](https://arxiv.org/abs/2312.07533)
- [Wang ve diğerleri — Qwen2-VL (arXiv:2409.12191)](https://arxiv.org/abs/2409.12191)
