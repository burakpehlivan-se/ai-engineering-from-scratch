# Sınırlı Öz-İyileştirme Tasarımları

> Araştırma, bir öz-iyileştirme döngüsünü (self-improvement loop) sınırlamak için dört ilkelde (primitive) yoğunlaştı. Her düzenlemeden önce ve sonra geçerli olmak zorunda olan resmi değişmezler (formal invariants). Değiştirilemeyen uyumsuzluk çapaları (alignment anchors). Her boyutun (güvenlik, adalet, sağlamlık) yalnızca performans değil, hepsinin eş zamanlı olarak geçerli olması gereken çoklu-hedef kısıtlamaları (multi-objective constraints). Tarihsel metriklerin yetenek kaybını (capability loss) gösterdiğinde döngüyü durduran gerileme tespiti (regression detection). Hiçbiri güvenliğin kanıtı değildir — bilgi kuramsal sonuçlar (Kolmogorov karmaşıklığı, Lob teoremi) herhangi bir sistemin kendi halefleri hakkında kanıtlayabileceklerini sınırlar. Bunlar sessiz maliyeti artıran hafifletmelerdir (mitigations).

**Tür:** Öğrenme
**Diller:** Python (stdlib, değişmez kontrolüyle sınırlı döngü)
**Önkoşullar:** Faz 15 · 07 (RSI), Faz 15 · 04 (DGM)
**Süre:** ~60 dakika

## Sorun

Ders 7'nin yarış simülatörü, küçük oran farklarının büyük boşluklara nasıl biriktiğini gösterdi. Ders 4'ün DGM vaka çalışması, döngülerin kendi değerlendiricilerini aktif olarak kandırabileceğini (game) gösterdi. Her iki sonuç da aynı mühendislik sorusuna işaret eder: öz-iyileştirme döngüsüne, döngü tarafından sessizce zayıflatılamayacak kısıtlamalar koyabilir misiniz?

ICLR 2026 RSI Atölyesi özeti (openreview.net/pdf?id=OsPQ6zTQXV) dört böyle ilkeyi belirliyor. Anthropic'in RSP v3.0'ı (Ders 19) ve DeepMind'ın FSF v3'ü (Ders 20) bunları yetenek eşiklerinde referans alır. Meta HyperAgents çalışması ve SAHOO (Mart 2026) gibi topluluk çerçeveleriproduction'da alt kümeleri uygular.

Dürüst çerçeve: bunlar hafifletmelerdir. Bilgi kuramsal sonuçlar, herhangi bir sistemin kendi halefi hakkında kanıtlayabileceklerini sınırlar ve hiçbir mevcut tasarım sorunu resmi olarak kapatmamıştır. İyi sınırlanmış bir döngü, sınırlanmamış olandan daha güvenlidir, mutlak anlamda güvenli değildir.

## Kavram

### İlke 1: resmi değişmezler (formal invariants)

Bir değişmez, her öz-değişiklikten önce ve sonra geçerli olmak zorunda olan bir özelliktir. Örnekler:

- Çıkış dağıtımdı (output distribution) sabit bir anayasa başlığına (constitutional header — Ders 17) koşulludur.
- Hiçbir araç çağrısı (tool call) yetkisiz bir uç noktaya (endpoint) gitmez.
- Bellek yazıları, logged ve imzalanmış bir yoldan geçer.
- Değerlendiricinin modül hash'i onaylanmış sürümle eşleşir.

Değişmezler, döngünün düzenleyemediği harici kod tarafından kontrol edilir. Önerilen bir değişiklik bir değişmezi ihlal ederse, reddedilir. Bu, DGM tarzı değerlendirici tahrif (tamper) modunu yakalar (Ders 4).

Zor kısım, güvenlik için gerekli ve makul sürede hesaplanabilir değişmezleri seçmektir. Aşırı tanımlama ilerlemeyi durdurur; eksik tanımlama, döngünün önemli özelliklerin yanından geçmesine izin verir.

### İlke 2: uyumsuzluk çapaları (alignment anchors)

Bir uyumsuzluk çapası, döngünün temel hedefinin (core objective) döngünün düzenleme yüzeyinin (edit surface) dışında sabitlendiği değişmez bir temsildir. Örnekler:

- Her çağrımada salt-okunur (read-only) bir konumdan yüklenen bir anayasa metni (Ders 17).
- Bağımsız erişim denetimiyle ayrı bir depoda (repository) bulunan bir değerlendirici.
- İnsan tarafından imzalanmış ve her döngüde yeniden doğrulanmış bir araç-izin beyanı (tool-permission manifest).

Çapanın rolü hedef sapmasını (objective drift) önlemektir. Döngü, hedefi nasıl takip ettiğini iyileştirebilir, ancak hedefin ne olduğunu düzenleyemez.

İnceliği olan hata modu: döngünün düzenleyemediği bir çapa, hâlâ okuma biçiminde sapmış bir döngü tarafından yeniden yorumlanabilir (reinterpret). Anayasal AI (Constitutional AI — Ders 17), yeni durumları ele almak için açıkça akla dayalıdır; bu akıl yürütme katmanı, yorumlama sapmasının (interpretation drift) yaşadığı yerdir. Çapalar gerekli, yeterli değildir.

### İlke 3: çoklu-hedef kısıtlamaları (multi-objective constraints)

Tek bir skor puanını optimize eden bir döngü kısayollar bulur. Aynı anda birden fazla sert kısıtlamayı (hard constraint) eş zamanlı olarak karşılaması gereken bir döngünün kullanabileceği daha az kısayol vardır. Tipik eksenler:

- Performans (görev düzeyinde benchmark)
- Güvenlik (kırmızı takım değerlendirmeleri, bilinen-kötüye ret oranı)
- Adalet (hassas alt gruplar üzerinde farklı etki sınırları — disparate-impact bounds)
- Sağlamlık (OOD test setleri, düşmanca girdi (adversarial input) işleme)

Bir değişiklik yalnızca her kısıtlama geçerliyse kabul edilir. Ders 13'ün maliyet valfi (cost governor), bunu maliyet kısıtlamalarıyla yığınlar (stack). Ders 18'in Llama Guard'ı bir güvenlik ekseni olarak bağlanır.

### İlke 4: gerileme tespiti (regression detection)

Her döngünün puanları tarihsel dağıtımlarla karşılaştırılır. Ayarlanan toleranstan öteye bir düşüş, döngüyü durdurur. Bu, aksi takdirde döngü "iyileştikçe" devam eden ortalamaya emilen sessiz yetenek kaybını yakalar.

Pratik bir uygulama: son N döngünün görev başına puanlarını saklayın. Her yeni döngü bir görev başına fark (delta) hesaplar. Herhangi bir delta bir eşiğin altına düşerse, döngü reddedilir ve bir insan inceler.

### Bilgi kuramsal sınırlar

Kolmogorov karmaşıklığı (complexity) ve Lob teoremi, bir sistemin kendi hakkında kanıtlayabileceklerine üst sınırlar koyar. Schmidhuber'ın resmi Godel Machine'i (Ders 4) bu sınırların en yükseğini hedefledi; hiç kimse önemsiz bir kanıtı tamamlamadı. Lob sonucu şunu söyler: bir sistem "kanıtlarsam X yapacağım"ı kanıtlanabilir şekilde inanıyorsa, kanıtlamadan X'i yapar — iyi bilinen bir öz-başvuru hatası (self-reference failure).

Primlerimiz için ima: bunlar güvenlik sorununu kapatamazlar. Sessiz maliyeti daha pahalı hale getirirler. Eksik bir kontrolü sessizce atlayacak kötü niyetli veya sapmış bir döngü, artık açıkça birini baltalamak zorundadır — bu daha tespit edilebilir bir imzadır.

### Örnek bir uygulama

Bir agent bir düzenleme öneriyor diyelim. Kapı yığını (gate stack):

1. Değişmez kontrolleri: modül hash'leri, araç-izin beyanı, anayasa başlığı.
2. Çapa kontrolü: hedef beyanı onaylanmış sürümle eşleşir (bayt-bayar veya anlamsal olarak).
3. Çoklu-hedef değerlendirmesi: performans, güvenlik, adalet, sağlamlık eksenleri.
4. Gerileme tespiti: hiçbir eksen toleranstan fazla düşmez.

Düzenlemenin gerçekleşmesi için dördünün de geçmesi gerekir. Tek bir başarısızlık bile döngüyü durdurur.

## Kullan

`code/main.py`, Ders 4'teki DGM tarzı oyuncak üzerinde, üzerine dört ilke katmanlanmış sınırlı bir öz-iyileştirme döngüsü çalıştırır. Her ilke ayrı ayrı devre dışı bırakılabilir veya etkinleştirilebilir. Gösterim, her ilkenin belirli bir hata sınıfını yakaladığını ve herhangi birinin kaldırılmasının o hata sınıfına izin verdiğini kanıtlar.

## Üret

`outputs/skill-bounded-loop-review.md`, önerilen bir sınırlı döngüyü (bounded loop) denetler ve iddia ettiğine karşın aslında hangi dört ilkeyi uyguladığını puanlar.

## Alıştırmalar

1. `code/main.py` dosyasını tüm primler etkin olarak çalıştırın. Döngünün ana metrikte hâlâ iyileştiğini, ancak hileye izin vermediğini doğrulayın.

2. Gerileme tespitini devre dışı bırakın. Buna sessiz yetenek kaybının kabul edilmesine yol açan bir girdi oluşturun.

3. Çoklu-hedef kısıtlamasını devre dışı bırakın. Döngünün performans ekseninde yakınlarken bir güvenlik ekseninin düştüğünü gösterin.

4. Bir kodlama agentı için bir uyumsuzluk çapası tasarlayın. Ne metin, nerede saklanır, nasıl kontrol edilir?

5. ICLR 2026 RSI Atölyesi özetini okuyun. Dört ilkeden birini seçin ve mevcut duruma Somut bir iyileştirme önerin.

## Anahtar Terimler

| Terim | Ne Söyleniyor | Aslında Ne Anlama Geliyor |
|---|---|---|
| Değişmez (Invariant) | "Her zaman doğru olan özellik" | Her düzenlemeden önce ve sonra harici kod tarafından kontrol edilen özellik |
| Uyumsuzluk çapası (Alignment anchor) | "Sabitlenmiş hedef" | Döngünün düzenleme yüzeyinin dışında, değiştirilemez temel hedef temsili |
| Çoklu-hedef kısıtlaması (Multi-objective constraint) | "Her eksen geçmeli" | Performans, güvenlik, adalet, sağlamlık — hepsi gerekli |
| Gerileme tespiti (Regression detection) | "Düşüşte dur" | Tarihsel metrik farkları yetenek kaybını gösterdiğinde döngüyü durdurur |
| Kolmogorov sınırı (Kolmogorov bound) | "Bilgi kuramsal sınır" | Bir sistemin kendi halefi hakkında kanıtlayabileceklerini sınırlar |
| Lob teoremi (Lob's theorem) | "Öz-başvuru tuzağı" | Sistem "yapmalıyım" üzerine kanıtlanmadan hareket edebilir |
| Kapı yığını (Gate stack) | "Katmanlı kontrol" | Birden fazla ilkenin birleşimi; her başarısızlık düzenlemeyi reddeder |
| Sınırlı iyileştirme (Bounded improvement) | "Kanıt değil, hafifletme" | Sessiz-maliyeti artırır; güvenlik sorununu kapatmaz |

## İleri Okuma

- [ICLR 2026 RSI Atölyesi özeti (OpenReview)](https://openreview.net/pdf?id=OsPQ6zTQXV) — dört-ilke yoğunlaşması.
- [Anthropic Sorumlu Ölçekleme Politikası v3.0](https://anthropic.com/responsible-scaling-policy/rsp-v3-0) — çoklu-hedef yetenek eşikleri.
- [DeepMind Sınır Güvenlik Çerçevesi v3](https://deepmind.google/blog/strengthening-our-frontier-safety-framework/) — aldatıcı uyumsuzluk izleme bir değişmez ilkesi olarak.
- [Schmidhuber (2003). Godel Machines](https://people.idsia.ch/~juergen/goedelmachine.html) — bu primlerin resmi-kanıt atası.
- [Anthropic — Claude'un Anayasası (Ocak 2026)](https://www.anthropic.com/news/claudes-constitution) — akla dayalı uyumsuzluk çapası.
