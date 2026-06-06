# Qwen-VL Ailesi ve Dinamik FPS Video

> Qwen-VL ailesi — Qwen-VL (2023), Qwen2-VL (2024), Qwen2.5-VL (2025), Qwen3-VL (2025) — 2026'da en etkili açık görüntü-dil modeli soyudur. Her nesil, geri kalanın on iki ay içinde kopyaladığı tek kararlı bir mimari bahis yaptı: M-RoPE aracılığıyla yerel dinamik çözünürlük, mutlak zaman hizalamalı dinamik-FPS örnekleme, ViT'de pencere dikkati (window attention) ve yapılandırılmış ajan çıktı biçimleri. Qwen3-VL'ye kadar tarif stabilleşmişti: yerel en boy oranı girdileriyle 2D-RoPE-ViT kodlayıcısı, büyük bir Qwen3 dil tabanına MLP projeksiyoncusu ve OCR, sapma (grounding) ve ajan davranışlarını birincil hedefler olarak vurgulayan eğitim aşamaları. Bu ders aileyi kronolojik olarak inceler, böylece her ayarın neden orada olduğunu anlarsınız.

**Tür:** Öğren
**Diller:** Python (stdlib, M-RoPE kodlayıcısı + dinamik-FPS örnekleme)
**Önkoşullar:** Faz 12 · 06 (patch-n'-pack)
**Süre:** ~120 dakika

## Öğrenme Hedefleri

- M-RoPE'nin üç eksenli döndürmelerini (zaman, yükseklik, genişlik) hesaplama ve neden üçünün de gerekli olduğunu açıklama.
- Bir video için dinamik-FPS örnekleme stratejisi seçme ve saniye başına token vs olay algılama doğruluğu hakkında akıl yürütme.
- Dört Qwen-VL nesil yükseltmesini sırasıyla ve her birinin neyi mümkün kıldığını adlandırma.
- Qwen2.5-VL tarzı JSON ajan çıktı biçimini bağlama ve bir VLM yanıtından yapılandırılmış araç çağırma (tool call) ayrıştırma.

## Sorun

Qwen-VL Ağustos 2023'te LLaVA-1.5 ve BLIP-2'ye doğrudan yanıt olarak geldi. Qwen ekibinin hedeflediği fark üç alandaydı: çözünürlük, video ve yapılandırılmış çıktı.

Çözünürlük: LLaVA-1.5 336x336'da çalıştı. Fotoğraflar için iyi, Çince bir fatura veya yoğun bir电子 tablo ekran görüntüsü için işe yaramaz. Qwen-VL'nin ilk yeniliği 448x448 ve sapma sınırlı kutu (bounding-box) çıkışıydı, modelin bir şeyleri göstermesine izin verdi.

Video: Video-LLaMA, kare başına kodlayıcıları üst üste yığarak LLM'e besledi. Kısa klipler için çalıştı, ama zamansal eksenin sinyal olduğu çok dakikalık videolar için çalışmadı. Qwen ekibi zamanı anlayan tek bir kodlayıcı istedi.

Yapılandırılmış çıktı: LLaVA serbest biçimli metin üretiyordu. Bir ajan JSON'a ihtiyaç duyuyordu. Qwen-VL, sınırlı kutu koordinatlarını metin olarak içeren açık JSON çıktı biçimlerinde eğitildi.

Her Qwen-VL nesili bu üç eksenden birini genişletir.

## Kavram

### Qwen-VL (Ağustos 2023)

İlk nesil: OpenCLIP ViT-bigG/14 kodlayıcı (2.5B parametre), LLaMA uyumlu Q-Former (256 sorgu ile 1 adım), Qwen-7B temel. Katkıları:

- 448x448 çözünürlük (o zamanlar açık VLM için SOTA).
- Sapma: açık koordinat token çıkışıyla görüntü-metin çiftlerinde eğitildi. "Kedi <box>(112, 204), (280, 344)</box> konumundadır".
- Daha baştan Çince + İngilizce çok dilli eğitim.

O zamanki kıyaslama testleri: İngilizce'de GPT-4V ile rekabetçi, Çince'de baskın. Sapma denetimi asıl manşetti.

### Qwen2-VL (Eylül 2024) — M-RoPE ve yerel çözünürlük

Qwen2-VL sabit çözünürlük + Q-Former yığınını yerel dinamik çözünürlüklü ViT kodlayıcısıyla değiştirdi. Temel değişiklikler:

- Yerel dinamik çözünürlük. ViT 28'le bölünebilir herhangi bir HxW'yi kabul eder (28'de 14 yama ile 2x uzamsal birleştirme). 1120x672 görüntü (40x24 birleştirilmiş yama) 960 görsel token üretir. Yeniden boyutlandırma, döşeme, küçük resim yok.
- M-RoPE (Çoklu Döndürme RoPE). Her token 1B yerine 3 boyutlu konum (t, h, w) taşır. Görüntüler için t=0, video için t = kare indeksi. RoPE sorgu/anahtar vektörlerini eksen başına frekansla döndürür. Konumsal gömme tablosu yok.
- MLP projeksiyoncusu. Q-Former'ı bırakın; birleştirilmiş yama token'ları üzerinde 2 katmanlı MLP kullanın.
- Dinamik FPS ile video. Video varsayılan olarak 1-2 FPS ile örneklenebilir ama model rastgele kare sayılarını kabul eder.

Sonuç: Qwen2-VL-7B several multimodal kıyaslama testinde GPT-4o ile eşleşti ve DocVQA'da (94.5 vs 88.4) yendi. Mimari değişiklik kararlı hamleydi.

### Qwen2.5-VL (Şubat 2025) — dinamik FPS + mutlak zaman

Qwen2.5-VL'nin büyük değişimi videodaydı. Dinamik FPS sadece "gerekirse daha fazla kare örnekle" değildir. Makale şu şekilde formalize etti:

- Mutlak zaman token'ları. Konumsal indeksler yerine (kare 0, 1, 2...) gerçek zaman damgaları kullanılır. "0:04'te kedi zıplıyor." Model `<time>0.04</time>` token'larının kare token'larıyla aralıklı olduğunu görür.
- Dinamik FPS. Yavaş çekim için 1 FPS, aksiyon için 4+ FPS ile örnekleme. Kullanıcı veya eğitmen seçer; M-RoPE uyarlanır.
- ViT'de pencere dikkati. Uzamsal dikkat, verimlilik için pencere sınırlıdır (bloklar içinde yerel); her birkaç katmanda küresel dikkat.
- Açık JSON çıktı biçimi. Araç çağırma verileriyle eğitildi: `{"tool": "click", "coords": [380, 220]}`. Kutudan çıktığı anda ajan-hazır.
- MRoPE-v2 ölçeklemesi. Konumlar maks girdi boyutuyla ölçeklenir, böylece 10 dakikalık bir video frekans aralığını tüketmez.

Kıyaslama testleri: Qwen2.5-VL-72B çoğu video kıyaslama testinde GPT-4o'yu yener, belgelerde Gemini 2.0 ile eşleşir ve GUI sapmasında (ScreenSpot: %84 doğruluk vs GPT-4o için %38) açık model SOTA'sını belirler.

### Qwen3-VL (Kasım 2025)

Qwen3-VL, yeniden icat etmek yerine birleştiren kademeli bir yükseltmedir: daha büyük LLM omurgası (Qwen3-72B), genişletilmiş eğitim verileri, geliştirilmiş OCR, Qwen3 "düşünme modu" ile daha güçlü akıl yürütme. ViT ve M-RoPE korunur. Makale mimari üzerinde veri ve eğitim geliştirmelerine odaklanır.

Soy dersi: 2025'e kadar Qwen-VL mimarisi stabilleşmişti. Sonraki nesiller ilkel birimleri değil, hesaplama ve veriyi ölçeklendirir.

### M-RoPE matematiksel olarak

Klasik RoPE, boyutu `d` olan bir sorgu `q`'yu `m` konumuyla eşleştirilmiş koordinatlar kullanarak döndürür:

```
q_rot[2i]   = q[2i]   * cos(m * theta_i) - q[2i+1] * sin(m * theta_i)
q_rot[2i+1] = q[2i]   * sin(m * theta_i) + q[2i+1] * cos(m * theta_i)
theta_i     = 10000^(-2i/d)
```

M-RoPE gizli boyutu üç şeride böler. `d = 96` diyelim. 32 boyutu zamana, 32'sini yüksekliğe, 32'sini genişliğe atayın. Her şerit kendi eksen konumuyla döndürülür. (t=5, h=10, w=20) konumundaki bir yama `R_t(5)`, `R_h(10)`, `R_w(20)` döndürmelerini üç şeridine uygular.

Metin token'ları `t = metin indeksi, h = 0, w = 0` (veya normalleştirilmiş bir seçim) kullanarak uyumluluk sağlar. Video kareleri `t = kare_zamanı, h = satır, w = sütun` kullanır. Tek görüntüler `t = 0` kullanır.

Avantaj: tek bir konum kodlaması metni, görüntüyü ve videoyu dalgalanma kodu veya farklı konum tabloları olmadan işler.

### Dinamik-FPS örnekleme mantığı

Süresi `T` saniye olan bir video ve hedef-token bütçesi `B` verildiğinde:

1. Karşılayabileceğiniz maksimum FPS'i hesaplayın: `fps_max = B / (T * kare başına token)`.
2. `fps <= fps_max` koşulunu karşılayan `{1, 2, 4, 8}` kümesinden bir hedef FPS seçin.
3. Hareket yüksekse (akış optik klonlaması veya açık kullanıcı istemi) daha yüksek FPS seçin. Hareket düşükse daha düşük seçin.
4. Seçilen FPS ile eşit aralıklı örnekleme; kareler arasında `<time>t</time>` token'ları ekleyin.

Qwen2.5-VL bu mantığı dolaylı olarak eğitir; çıkarım sırasında kullanıcı `fps` parametresiyle kontrol eder. 81 token/kare ile 4 FPS'te 60 saniyelik bir aksiyon dizisi = 19440 token, 32k bağlamda yönetilebilir.

### Yapılandırılmış ajan çıkışı

Qwen2.5-VL'nin ajan eğitimi açıkça yapılandırılmış araç çağrılara odaklanır:

```
{
  "tool": "mouse_click",
  "coords": [1024, 512],
  "button": "left",
  "modifier": null
}
```

#### Açıklama
Ayrıştırma deterministiktir: JSON.parse modelin çıktısı üzerinde. Serbest biçimli "1024, 512'de tıkla" ile karşılaştırıldığında regex ve belirsizlik işleme gerektirirdi. Qwen2.5-VL'nin ScreenSpot puanlarının Qwen2-VL'nin %55'inden %84'e sıçramasının nedeni budur.

## Kullan

`code/main.py` şunları uygular:

- Metin, görüntü yamaları ve video karelerini karıştıran paketlenmiş bir dizi için M-RoPE konum hesaplaması.
- Dinamik-FPS örnekleme: (süre, bütçe, hareket_düzeyi) verildiğinde FPS seçer ve kare zaman damgaları üretir.
- Koordinat alanları içeren araç çağırma yanıtlarını işleyen oyuncu bir Qwen2.5-VL JSON-çıktı ayrıştırıcısı.

Çalıştırın, ardından 5 dakikalık bir videoda sabit-FPS'yi dinamik-FPS ile değiştirdiğinizde farkı hissedin.

## Teslimat

Bu ders `outputs/skill-qwen-vl-pipeline-designer.md` dosyasını üretir. Bir video görevi (izleme, ajan, eylem tanıma, erişilebilirlik) verildiğinde, Qwen2.5-VL yapılandırmasını (kare bütçesi, FPS stratejisi, pencere-dikkati bayrağı, ajan-çıktı modu) ve bir gecikme tahmini üretir. Bir video ürünü için Qwen-VL ailesi modeli her dağıttığınızda bunu kullanın.

## Alıştırmalar

1. (t=3, h=5, w=7) konumunda 48 gizli (şerit başına 16, temel theta 10000) olan bir yama için M-RoPE döndürmelerini hesaplayın. Her şeritten ilk üç çift için döndürme açılarını gösterin.

2. 1 FPS ile 10 dakikalık güvenlik kamerası kaydı kaç kare üretir? 384 çözünürlükte 3x havuzlamayla toplam kaç token vardır? Qwen2.5-VL'nin varsayılan 32k bağlamı bunu işler mi?

3. 30 saniyelik bir tenis rallisi, 30 saniyelik bir tarif demosu ve 30 saniyelik bir arayüz-ajan kaydı için FPS seçin. Her birini dinamik-FPS mantığıyla gerekçelendirin.

4. Qwen2.5-VL Q-Former'ı tamamen bırakıyor. 2025'te basit bir MLP neden çalışıyor da 2023'te çalışmıyordu? (İpucu: veri ölçeği ve kodlayıcı kalitesi.)

5. Üç Qwen2.5-VL JSON araç çağırma çıktısını Python sözlüklerine ayrıştırın. Hatalı JSON'da ne başarısız olur ve Qwen cookbook'u hangi kurtarma stratejisini önerir?

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| M-RoPE | "Çoklu Döndürme RoPE" | Gizli boyutta zaman, yükseklik ve genişlik şeritleri olan 3B döndürme konum gömmesi |
| Dinamik FPS | "Akıllı örnekleme" | Hareket, süre ve token bütçesine göre video başına seçilen kare örnekleme hızı |
| Mutlak zaman token'ı | "Zaman damgası token'ı" | `<time>t</time>` dizide aralanır, böylece model kare indeksi yerine gerçek saniyeleri görür |
| Pencere dikkati | "Yerel dikkat" | Hız için küçük pencerelere kısıtlı uzamsal öz-dikkat; periyodik olarak küresel dikkat eklenir |
| Yapılandırılmış ajan çıkışı | "JSON modu" | VLM'in koordinat ve araç adlarıyla ayrıştırılabilir JSON üretmesini öğreten eğitim verisi denetimi |
| min_pixels / max_pixels | "Çözünürlük sınırları" | İsteğe bağlı Qwen2.5-VL kontrolleri, toplam piksel sayısını ve dolayısıyla token sayısını sınırlar |
| Sapma (Grounding) | "Noktalama" | Sınır kutusu koordinatlarını metin token'ları olarak çıkarma; Qwen-VL v1'den beri kullanılır |

## İleri Okuma

- [Bai ve diğerleri — Qwen-VL (arXiv:2308.12966)](https://arxiv.org/abs/2308.12966)
- [Wang ve diğerleri — Qwen2-VL (arXiv:2409.12191)](https://arxiv.org/abs/2409.12191)
- [Qwen Ekibi — Qwen2.5-VL Teknik Raporu (arXiv:2502.13923)](https://arxiv.org/abs/2502.13923)
- [Qwen Ekibi — Qwen3-VL (arXiv:2511.21631)](https://arxiv.org/abs/2511.21631)
- [Zhu ve diğerleri — InternVL3 (arXiv:2504.10479)](https://arxiv.org/abs/2504.10479)
