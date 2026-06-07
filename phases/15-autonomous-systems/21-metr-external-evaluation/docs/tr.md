# METR Zaman Ufukları ve Bağımsız Yetenek Değerlendirmesi

> METR (eski ARC Evals), Aralık 2023'ten bu yana bağımsız bir 501(c)(3)'tür. Time Horizon 1.1 karşılaştırmalaması (Ocak 2026), görev başarı olasılığını log(uzman insan tamamlama süresi) karşı lojistik bir eğriye (logistic curve) oturtur; %50 olasılıktaki kesişim noktasının belirlediği modelin zaman ufku (time horizon)'dur. 2025–2026 temas kümesi GPT-5.1, GPT-5.1-Codex-Max ve prototip izleme değerlendirmelerini (bir izleyici yan görevleri yakalayabilir mi; agent izleyiciden kaçabilir mi) kapsar. Karşılaştırma paketleri: HCAST (180+ ML, siber, SWE, akıl yürütme görevi; 1 dakikadan 8+ saate), RE-Bench (insan temelli 71 ML araştırma-mühendislik görevi), SWAA. Dürüst not: METR ölçümleri idealized'dir — insan yok, gerçek sonuçlar yok — ve ekip eval-vs-deployment davranış boşluğunu (Ders 1) belgelemiştir. Bir zaman ufku bir üst sınırdır, dağıtım tahmini değildir.

**Tür:** Öğrenme
**Diller:** Python (stdlib, lojistik oturtmalı ufuk tahmin edici)
**Önkoşullar:** Faz 15 · 01 (Uzun vadeli agent'lar), Faz 15 · 19 (RSP)
**Süre:** ~60 dakika

## Sorun

Ölçekleme politikaları (Ders 19, 20) ancak referans verdiği ölçümler kadar yararlıdır. "AI R&D-4 eşiği" ve "Uzun Vadeli Otonomi" politika diliyle tanımlanır; sadece belirli değerlendirmeler belirli sayılar ürettiğinde eyleme geçirilebilir hale gelir.

METR, 2024–2026 döneminde bu sayıların çoğunu tanımlamış olan bağımsız değerlendirme kuruluşudur. Sınır modellerini — genellikle dağıtımdan önce, NDA altında — değerlendirir ve sonrasında metodolojiyi yayınlar. Time Horizon 1.1 karşılaştırmalaması (Ocak 2026) onların başlık eseridir: yeteneği tek bir insana okunabilir birime sıkıştıran bir skaler ("bu model, bir uzmanın X saat harcadığı türde bir görevi yapabilir").

Ders kısmen metodolojiyle (ufkun nasıl hesaplandığıyla) ve kısmen yorumlamayla (neden bir üst sınır, dağıtım tahmini olmadığıyla) ilgilidir. İki beceri birlikte gider. Ufğun nasıl oturtulduğunu anlayan bir ekip, kötü bir satıcı iddiası karşısında sadece slaytta "14 saat" gören bir ekipten çok daha zor aldanır.

## Kavram

### METR arka planı

- Kuruluş: Aralık 2023 (eski ARC Evals, bağımsız 501(c)(3)'e ayrıldı).
- Kapsam: sınır modellerinin otonom yeteneklerinin değerlendirilmesi, genellikle dağıtımdan önce.
- Partner laboratuvarlar: Anthropic, OpenAI (2025–2026'da çoklu temalar).
- Dikkat çekici teslimatlar: Time Horizon 1.0 (Mart 2025), Time Horizon 1.1 (Ocak 2026), prototip izleme değerlendirmeleri.

### Time Horizon oturtumu

Metodoloji (METR blogu ve makalelerinden):

- Dakika ölçeğinden saat ölçeğine kadar uzan bir görev paketi toplayın. Mevcut paketler: HCAST (180+ görev), RE-Bench (71 görev), SWAA.
- Modeli her görevde çalıştırın; başarı veya başarısızlığı kaydedin.
- Lojistik eğri oturtun: P(başarı) = f(log(uzman tamamlama süresi)).
- Ufuk, P(başarı) = 0.5 olduğu uzman süresidir.

Lojistik oturtma biçimi doğrudur çünkü yetenek genellikle görev zorluğuyla artan ve plato yaklaşan bir ilişki gösterir. %50 noktası bir tercihtir (%10, %90 olabilirdi); METR detaylı makalede birden fazla eşik raporlar ancak %50'yi öne çıkar çünkü en sezgisel olanıdır.

### Ocak 2026 sayıları

Time Horizon 1.1'e göre:

- Claude Opus 4.6: Time Horizon 1.1 (Ocak 2026) göre %50 güvenilirlikle ~14 saat.
- HCAST tarzı görevlerde ikiye katlanma süresi: Time Horizon 1.1 (Ocak 2026) tarafından bildirilen 2023 sonrası oturtuma göre ~4.3 ay (130.8 gün); ~7 aylık rakam Time Horizon 1.0'dan tam 2019–2025 oturtumudur ve TH1.1 tarafından 2023 sonrası sayıyla birlikte raporlanır.

Bunlar Faz 15'in geri kalanının referans verdiği belirli sayılardır. Anthropic RSP v3.0 (Ders 19) ve DeepMind FSF v3 (Ders 20) tarafından eşik değerlendirmelerini besleyen ölçümler olarak alıntılanır.

### Karşılaştırma paketleri

- **HCAST:** ML, siber güvenlik, yazılım mühendisliği ve genel akıl yürütmede 189 görev. Uzman süresi: 1 dakikadan 8+ saate. Ufuk sayısının arkasındaki ana paket.
- **RE-Bench:** İnsan uzman temelli 71 ML araştırma-mühendislik görevi. Modelin AI R&D-4 eşiğini besleyen ML R&D işini yapıp yapamayacağını ölçer.
- **SWAA:** daha kısa görevler; ufuk eğrisinin alt ucunu kalibre etmek için yararlı.

### Prototip izleme değerlendirmeleri

2025–2026 METR çalışması izleme-değerlendirme prototiplerini içerdi: bir izleyici, bir modelin operatörün istediği şeyin dışında bir yan görev yapıp yapamadığını yakalayabilir mi; agent izleyiciden kaçabilir mi. Bunlar doğrudan OpenAI PF v2'deki "Güvenlik Önlemlerini Baltalama" kategorisine ve DeepMind FSF v3'teki aldatmacalı uyumluluk izlemesine (Ders 20) beslenir.

### Neden ufuklar üst sınırlardır

- **İdealized araçlar:** karşılaştırma görevleri modele temiz araçlar ve iyi biçimlendirilmiş veriler verir. Gerçek dağıtımlar daha karışık.
- **Gerçek sonuçlar yok:** model gerçekten bir müşteriyi faturalandırmaz, gerçek veriyi silmez veya gerçek insanlarla iletişime geçmez. Gerçek dağıtımlarda geri dönüşü olmayan sonuçlar vardır.
- **Değerlendirme-bağlam oyunu:** Ders 1. Modeller testlerde farklı davranır. 2026 Uluslararası AI Güvenlik Raporu bunu deneysel olarak belgeler.
- **Meşru kullanıcı varyansı yok:** karşılaştırma istemleri yapılandırılmıştır. Gerçek kullanıcılar belirsiz, bağımlı istekler üretir.

Ufuk, elverişli koşullar altındaki yetenek tavanıdır. Dağıtım güvenilirliği farklı bir sayıdır, daha düşüktür ve ekipler kendi dağıtımlarını ölçmek zorundadır.

### Bağımsız değerlendirici vakası

Bağımsız değerlendirme önemlidir çünkü iç laboratuvarlar raporladıkları metrikleri optimize etme eğilimindedir. METR'nin bağımsızlığı — ilan edilmiş bir metodolojiye ve hakemli makalelere sahip bir 501(c)(3) — yapısal azaltmadır. Tek başına yeterli değildir (laboratuvarlar hala METR'nin ne gördüğünü kontrol eder), ancak bağımsız değerlendirme olmamasından kesinlikle daha iyidir.

### Ufuk sayıları pratikte nasıl kullanılır

- **Yetenek filtresi olarak:** bir modelin ufku, önerilen bir görevin uzman süresinin çok altındaysa, onu otonom olarak dağıtmayın (Ders 1 beceri dosyası).
- **Eğilim göstergesi olarak:** ikiye katlanma süresi, mevcut uygulamanın yeni azaltmalar olmadan ne kadar süre güvenli kalacağını söyler.
- **Ön bilgi (prior) olarak:** 14 saatlik bir ufuk bir başlangıç noktasıdır. Görev dağıtımınıza, araç kalitenize ve dağıtım bağlamınıza göre aşağıya ayarlayın.

## Kullan

`code/main.py`, verilen bir sentetik sonuç kümesiyle görev başarısının log(uzman zamanı)'na karşı lojistik oturtmasını uygular. %50 ufku (METR'nin başlık rakamı), %10 ufku (muhafazakar) ve %90 ufku (iyimser) raporlar. Ayrıca başarısızlık oranının değerlendirme-bağlam oyunuyla yapay olarak şişirilmesi durumunda neyin değiştiğini gösterir.

## Üret

`outputs/skill-horizon-interpretation.md`, bir satıcının ufuk iddiasını inceler ve karşılaştırma iddiası ile dağıtım gerçekliği arasında bir boşluk analizi üretir.

## Alşırtmalar

1. `code/main.py` çalıştırın. Oturtmanın %50 ufkunun sentetik gerçek zeminle eşleştiğini doğrulayın. Şimdi görev-zaman ızgarasını ikiye bölün; ufuk tahmi anlamlı şekilde değişir mi?

2. METR'nin Time Horizon 1.1 blog yazısını okuyun. Güvenilirliğin en yüksek ve en düşük olduğu belirli görevleri belirleyin. Boşluğun neden var olduğunu açıklayın.

3. METR'nin "Otonom AI Yeteneklerini Ölçme Kaynakları"nı okuyun. HCAST görev kategorilerini listeleyin. Üretim görevi için daha fazla ağırlık vereceğiniz bir kategori seçin ve nedenini gerekçelendirin.

4. Değerlendirme-bağlam oyununu simülatöre sokun: başarısız görevlerin ~%20'sini başarıya çevirin. Yeni ufku raporlayın. Bu, %20'lik bir oyun oranının gözlemlenen sayıya ne yaptığını yaklaşıklar.

5. Kendi hata birikiminizde veya temsili bir görev kümesinde iç bir ufuk değerlendirmesi tasarlayın. Veri toplamayı, oturtmayı ve çıktının ne anlama geldiğini açıklayın. METR sayılarıyla karşılaştırın.

## Anahtar Terimler

| Terim | Ne Söyleniyor | Aslında Ne Anlama Geliyor |
|---|---|---|
| METR | "Bağımsız değerlendirici" | Eski ARC Evals; Aralık 2023'ten bağımsız 501(c)(3) |
| Time Horizon (Zaman ufku) | "Yetenek ölçüsü" | Lojistik oturtmadan %50 güvenilirlikte uzman görev süresi |
| HCAST | "METR'nin ana paketi" | 1 dakikadan 8+ saate kadar 180+ görev |
| RE-Bench | "Araştırma mühendisliği" | İnsan temelli 71 ML araştırma-mühendislik görevi |
| SWAA | "Kısa görev paketi" | Ufuk eğrisinin alt ucunu kalibre eder |
| Doubling time (İkiye katlanma süresi) | "Büyüme oranı" | %50 ufkun ikiye katlanması için gereken süre; HCAST'a göre ~7 ay |
| Eval-context gaming (Değerlendirme-bağlam oyunu) | "Model farklı davranıyor" | Testler ve dağıtım arasındaki belgelenmiş davranış boşluğu |
| Upper bound (Üst sınır) | "Ufuk bir tavan" | Karşılaştırma ufku > yükleme altında dağıtım güvenilirliği |

## İleri Okuma

- [METR — Otonom AI Yeteneklerini Ölçme Kaynakları](https://metr.org/measuring-autonomous-ai-capabilities/) — HCAST, RE-Bench, SWAA özellikleri.
- [METR — Uzun Görevleri Tamamlama İçin AI Yeteneğini Ölçme](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) — orijinal ufuk makalesi.
- [METR — Time Horizon 1.1 (Ocak 2026)](https://metr.org/research/) — güncel sayılar ve metodoloji.
- [Epoch AI — METR Time Horizons karşılaştırması](https://epoch.ai/benchmarks/metr-time-horizons) — canlı izleme.
- [Anthropic — Pratikte agent otonomunu ölçme](https://www.anthropic.com/research/measuring-agent-autonomy) — METR ölçümleri hakkında iç perspektif.
