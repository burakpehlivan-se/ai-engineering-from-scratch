# Her Çözünürlükte Görüntü: Patch-n'-Pack ve NaFlex

> Gerçek görüntüler 224x224 kare değildir. Bir makbuz 9:16, bir grafik 16:9, tıbbi bir tarama 4096x4096 olabilir, mobil ekran görüntüsü 9:19.5'tir. 2024 öncesi VLM cevabı — her şeyi sabit bir kareye yeniden boyutlandırma — OCR, belge anlama ve yüksek çözünürlüklü sahne ayrıştırmasını mümkün kılan sinyali atıyordu. NaViT (Google, 2023), değişken çözünürlüklü yamaları blok çapraz (block-diagonal) maskelemeyle tek bir transformer toplu işine paketleyebileceğinizi gösterdi. Qwen2-VL'nin M-RoPE'si (2024) mutlak konumsal tabloları tamamen bıraktı. LLaVA-NeXT'in AnyRes'i yüksek çözünürlüklü görüntüleri temel + alt görüntülere döşedi. SigLIP 2'nin NaFlex çeşidi (2025) artık her en boy oranını sunmak isteyen açık VLM'ler için varsayılan kodlayıcıdır. Bu ders patch-n'-pack'i baştan sona uygular.

**Tür:** İnşa Et
**Diller:** Python (stdlib, yama paketleyici + blok çapraz maske)
**Önkoşullar:** Faz 12 · 01 (ViT yamaları), Faz 12 · 05 (LLaVA)
**Süre:** ~120 dakika

## Öğrenme Hedefleri

- Değişken çözünürlüklü görüntülerden oluşan bir toplu işin yamalarını tek bir diziye paketleme ve blok çapraz dikkat maskesini inşa etme.
- Verilen bir görev için AnyRes döşeme (LLaVA-NeXT), NaFlex (SigLIP 2) ve M-RoPE (Qwen2-VL) arasında seçim yapma.
- Yeniden boyutlandırma yapmadan OCR, grafikler ve fotoğrafçılık için token bütçelerini hesaplama.
- Kare yeniden boyutlandırmanın üç başarısızlık modunu adlandırma: sıkıştırılmış metin, kırpılmış içerik, dolgu (padding) üzerinde boşa harcanan token'lar.

## Sorun

Transformer'lar bir dizi bekler. Bir toplu iş, aynı uzunluktaki dizilerin bir yığınıdır. Görüntüleriniz 224x224 ise her seferinde 196 yama token'ı alırsınız, dolgu gerekmez, iş biter. 224'te eğitin, 224'te çıkarım yapın, çözünürlük hakkında bir daha düşünmeyin.

Dünya işbirliği yapmıyor. Belgeler dikeytir (8.5x11 inç, yaklaşık 2:3). Grafik ekran görüntüleri yataydır (16:9). Makbuzlar uzun ve dardır (1:3). Tıbbi görüntüleme 2048x2048 veya daha büyük gelir. Mobil cihaz ekran görüntüleri 1170x2532'dir (0.46:1).

2024 öncesi üç seçenek ve her birinin neden başarısız olduğu:

1. Sabit bir kareye (224x224 veya 336x336) yeniden boyutlandırma. Sıkıştırma metin ve yüzleri bozar. Küçültme grafik etiketlerini ve OCR içeriğini yok eder. LLaVA-1.5'ye kadar standart uygulama.
2. Sabit en boy oranına kırpma. Görüntünün çoğunu atarsınız ve kırpma konumunu seçmek kendi başına bir görüntü sorunudur.
3. En uzun kenara dolgu. Bozulmayı düzeltir ama dikey görüntülerde token'ların %50+'ını dolguya boşa harcar. Tüm bu dolgu token'larında karesel dikkat maliyeti.

2024-2025 cevabı: transformer'ın görüntüdeki yerel çözünürlükte yamaları yemesine izin verin ve heterojen bir toplu işi boşa harcanmadan tek bir diziye nasıl paketleyeceğinizi bulun.

## Kavram

### NaViT ve patch-n'-pack

NaViT (Dehghani ve diğerleri, 2023) bunun ölçekte çalıştığını gösteren makaleydi. Fikir mekaniktir:

1. Toplu işteki her görüntü için seçilen bir yama boyutuyla (ör. 14) yerel yama ızgarasını hesaplayın.
2. Her görüntünün yamalarını kendi değişken uzunluklu dizisine düzleştirin.
3. Tüm görüntülerin yamalarını toplu iş için tek bir uzun dizide birleştirin.
4. Görüntü A'nın yamalarının yalnızca görüntü A içinde dikkat etmesini sağlayan blok çapraz dikkat maskesi oluşturun.
5. Yama başına konum bilgisi taşıyın (2D RoPE veya kesirli konum gömmeleri).

336x336 (576 token), 224x224 (256 token) ve 448x336 (768 token) boyutlarında üç görüntüden oluşan bir toplu iş, 1600x1600 blok çapraz maskeli tek bir 1600 tokenlık dizi olur. Dolgu yok. Boşa harcanan hesaplama yok. Transformer rastgele en boy oranlarını işler.

NaViT ayrıca eğitim sırasında kesirli yama bırakmayı da tanıttı — toplu iş boyunca rastgele %50 yama bırak hem düzenlileştirir (regularize) hem de eğitimi hızlandırır. SigLIP 2 bunu devraldı.

### AnyRes (LLaVA-NeXT)

LLaVA-NeXT'in AnyRes'i pragmatik alternatiftir. Yüksek çözünürlüklü bir görüntü ve sabit bir kodlayıcı (CLIP veya SigLIP 336'ta) verildiğinde, görüntüyü döşeyin:

1. Önceden tanımlı bir kümden en uygun ızgara düzenini seçin — (1x1), (1x2), (2x1), (1x3), (3x1), (2x2) vb.
2. Tam görüntüyü ızgaraya döşeyin; her döşeme 336x336 kırpma olur.
3. Ayrıca bir küçük resim (thumbnail) üretin: tüm görüntü 336x336'ya yeniden boyutlandırılmış küresel bağlam token'ı olarak.
4. Her döşemeyi donmuş 336 kodlayıcıyla kodlayın. Döşeme token'ları + küçük resim token'larını birleştirin.

672x672 görüntü için 2x2 ızgara artı küçük resim: 4 * 576 + 576 = 2880 görsel token. Pahalı ama etkili — LLM hem yerel ayrıntıyı hem de küresel bağlamı görür.

AnyRes, kodlayıcınız donmuşsa ve yalnızca bir çözünürlüğü destekliyse tercih edilen yoldur. Büyük görüntüler için token sayısını patlatır (1344x1344 görüntü 4x4 ızgarada 9216 + 576 ≈ 9800 token, 8k LLM bağlamının çoğunu doldurur).

### M-RoPE (Qwen2-VL)

Qwen2-VL Çoklu Döndürme Konumsal Gömmeyi (Multimodal Rotary Position Embedding) tanıttı. NaViT'nin kesirli konumları veya AnyRes'in döşeme-küçük resim'i yerine, her yama 3 boyutlu bir konum (zaman, yükseklik, genişlik) taşır. Sorgu/anahtar döndürmeleri rastgele H, W ve uzunluk zamanlamasını (temporal length) işler.

M-RoPE, yeniden eğitmeden yerel dinamik çözünürlüğü sunar. Çıkarım sırasında herhangi bir HxW görüntüsü beslersiniz, yama kodlayıcısı H/14 x W/14 token üretir, her token (t=0, r=satır, c=sütun) konumunu alır, RoPE doğru frekanslarla dikkati döndürür, bitti. Qwen2.5-VL ve Qwen3-VL buna devam eder. InternVL3'ün V2PE'si modalite başına değişken kodlama ile aynı fikirdir.

AnyRes'ten farklı olarak M-RoPE, yerel çözünürlükte O(H x W / P^2) token'dır — çarpanlı döşeme overhead'i yoktur. NaViT'den farklı olarak hâlâ ileri geçiş başına tek görüntü bekler. Çözünürlükler arası toplu iş hâlâ patch-n'-pack gerektirir.

### NaFlex (SigLIP 2)

NaFlex, SigLIP 2 kontrol noktasının esnek-yerel (native-flex) modudur. Tek bir model çıkarım sırasında birden fazla dizi uzunluğunu (256, 729, 1024 token) sunar. İç olarak NaViT tarzı patch-n'-pack'i eğitim sırasında kullanır ve yama başına mutlak kesirli konumlar kullanır. Satış noktası: tek kontrol noktası, göreve göre çıkarım sırasında token bütçenizi seçin.

Anlamsal bir görev (sınıflandırma, geri çağırma) için 256 token. OCR veya grafik anlama için 1024 token. Yeniden eğitim yok.

### Paketleme maskesi

Birçok uygulamanın takıldığı yer blok çapraz maskedir. `i=0.. B-1` görüntülerini ve `n_i` uzunluklarını kapsayan `N_total` uzunluğunda paketlenmiş bir dizi için, `(N_total, N_total)` boyutunda `M` maskesi, her iki indeks de aynı görüntü bloğundaysa 1, aksi halde 0'dır. Kümelenmiş uzunluk listesinden oluşturabilirsiniz:

```
offsets = [0, n_0, n_0+n_1, ..., N_total]
M[i, j] = 1 iff there exists b where offsets[b] <= i < offsets[b+1] and offsets[b] <= j < offsets[b+1]
```

#### Açıklama
Bu PyTorch'ta `torch.block_diag` ile veya açık toplama ile tek satırdır. FlashAttention'ın değişken uzunluk yolu (`cu_seqlens`) maskeyi tamamen atlar ve kümelenmiş uzunluk tensörünü doğrudan kullanarak diziler içinde dikkat uygular — tipik toplu işler için yoğun maskeden ~10x daha hızlıdır.

### Token bütçeleri

Görevinize göre stratejinizi seçin:

- OCR / belgeler: 1024-4096 token. 1024'te SigLIP 2 NaFlex veya AnyRes 3x3 + küçük resim.
- Grafikler ve arayüz: 384-448 yerel çözünürlükte 729-1024 token. Maks piksel tavanı ile Qwen2.5-VL dinamik çözünürlüğü.
- Doğal fotoğraflar: 256-576 token yeterlidir. Alt LLM yeterince görür. İçerik yoğunluğunun yüksek olduğu yerlerde token için ödeme yapın.
- Video: Uzamsal havuzlamadan sonra kare başına 64-128 token, 2-8 FPS. Ders 12.17 bunu kapsar.

2026 üretim kuralı: görev başına maks piksel tavanı seçin, yerel en boy oranında o tavana kadar kodlayın, toplu işi paketleyin ve dolguyu atlayın. Qwen2.5-VL tam olarak bu ayarı sunar `min_pixels` ve `max_pixels` ile.

## Kullan

`code/main.py`, tamsayı piksel koordinatlarıyla heterojen bir toplu iş için patch-n'-pack'i uygular:

- Bir (H, W) görüntü boyutları listesi alır.
- Her görüntünün yama boyutu 14'te yama dizi uzunluğunu hesaplar.
- Toplam uzunluk `sum(n_i)` olan tek bir diziye paketler.
- Blok çapraz dikkat maskesini (netlik için yoğun) oluşturur.
- Paketlenmiş maliyeti kare yeniden boyutlandırma ve AnyRes döşemesiyle karşılaştırır.
- Karışık bir toplu iş (makbuz, grafik, ekran görüntüsü, fotoğraf) için token bütçesi tablosu yazdırır.

Çalıştırın. Düşen sayılar, 2026'nın her açık VLM'inin patch-n'-pack kullanmasının nedenidir.

## Teslimat

Bu ders `outputs/skill-resolution-budget-planner.md` dosyasını üretir. Karışık en boy oranlı bir iş yükü (OCR, grafikler, fotoğraflar, video kareleri) ve toplam token bütçesi verildiğinde doğru stratejiyi seçer (NaFlex, AnyRes, M-RoPE veya sabit kare) ve istek başına yapılandırma üretir. Bir VLM'i bir ürün için boyutlandırırken bu beceriyi kullanın — gecikme bütçelerini öldüren sessiz 10x token patlamasını önler.

## Alıştırmalar

1. Bir makbuz 600x1500 (1:2.5). Yama boyutu 14'te kaç yerel çözünürlük token'ı vardır? 336'a kare yeniden boyutlandırmadan sonra kaç tanesi vardır? Pratikte hangisi daha fazla OCR doğruluğu kaybeder?

2. 256, 576, 729, 1024 uzunluklarında dört görüntüden oluşan bir toplu iş için blok çapraz maskeyi oluşturun. Dikkat matrisinin 2585x2585 olduğunu ve tam olarak `256^2 + 576^2 + 729^2 + 1024^2` sıfır-dışı girdiye sahip olduğunu doğrulayın.

3. 1792x896 görüntü için yama 14'te karşılaştırın: (a) 336'a kare yeniden boyutlandırıp kodlayın, (b) AnyRes 2x1 + küçük resim, (c) yerel çözünürlükte M-RoPE. Hangisi en az token'ı kullanır? Hangisi en fazla ayrıntıyı korur?

4. Kesirli yama bırakmayı (fractional patch dropping) uygulayın: paketlenmiş bir dizi verildiğinde, token'ların %50'sini rastgele olarak bırakın ve blok çapraz maskesini buna göre güncelleyin. Maskenin seyreklik (sparsity) değişimini ölçün.

5. Qwen2-VL makalesinin Bölüm 3.2'sini okuyun (arXiv:2409.12191). `min_pixels` ve `max_pixels`'in neyi kontrol ettiğini ve her iki sınırın neden önemli olduğunu iki cümleyle açıklayın.

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Patch-n'-pack | "NaViT tarzı paketleme" | Farklı görüntülerden değişken uzunluklu yama dizilerini tek bir toplu iş boyutuna birleştirme |
| Blok çapraz maske | "Paketleme maskesi" | Her görüntünün yamalarının yalnızca kendilerine dikkat etmesini sağlayan dikkat maskesi |
| AnyRes | "LLaVA-NeXT döşeme" | Yüksek çözünürlüklü görüntüleri sabit boyutlu döşemeler ızgarasına ve küresel küçük resime böler; her döşemeyi sabit kodlayıcıyla kodlar |
| NaFlex | "SigLIP 2 esnek-yerel" | Çıkarım sırasında yeniden eğitim yapmadan 256/729/1024 token bütçesi sunan tek SigLIP 2 kontrol noktası |
| M-RoPE | "Çoklu Döndürme RoPE" | (zaman, satır, sütun) 3 boyutlu döndürme konum kodlaması; rastgele H, W, T'yi konum tablosu olmadan işler |
| cu_seqlens | "FlashAttention paketleme" | Yoğun blok çapraz maske yerine FlashAttention varlen yolunun kullandığı kümelenmiş uzunluk tensörü |
| min_pixels / max_pixels | "Çözünürlük sınırları" | Qwen2.5-VL istek başına, çok küçük veya çok büyük girdilerde token sayısını sınırlayan ayarlar |
| Görsel token bütçesi | "Görüntü başına kaç token" | Görüntü başına üretilen yama token'larının yaklaşık sayısı; LLM istem bütçesini ve dikkat maliyetini belirler |

## İleri Okuma

- [Dehghani ve diğerleri — Patch n' Pack: NaViT (arXiv:2307.06304)](https://arxiv.org/abs/2307.06304)
- [Wang ve diğerleri — Qwen2-VL (arXiv:2409.12191)](https://arxiv.org/abs/2409.12191)
- [Laurençon ve diğerleri — Görüntü-dil modelleri inşa ederken ne önemlidir? (Idefics2, arXiv:2405.02246)](https://arxiv.org/abs/2405.02246)
- [Tschannen ve diğerleri — SigLIP 2 (arXiv:2502.14786)](https://arxiv.org/abs/2502.14786)
- [Qwen Ekibi — Qwen2.5-VL Teknik Raporu (arXiv:2502.13923)](https://arxiv.org/abs/2502.13923)
