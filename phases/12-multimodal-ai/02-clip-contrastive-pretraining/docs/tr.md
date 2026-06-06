# CLIP ve Karşıtlıklı Görüntü-Dil Ön-Eğitimi

> OpenAI'ın CLIP'i (2021) beş yılı besleyecek kadar büyük tek bir fikri kanıtladı: bir görüntü kodlayıcısı ve bir metin kodlayıcısını yalnızca gürültülü web görüntü-açıklama çiftleri ve bir karşıtlık kaybı (contrastive loss) ile aynı vektör uzayında hizalayın. Sıfır denetimli etiket. 400M çift. Elde edilen gömme uzayı (embedding space) zero-shot sınıflandırma, görüntü-metin geri çağırma yapar ve 2026'nın her VLM'ine görüntü kulesi olarak bağlanır. SigLIP 2 (2025) softmax'i sigmoid ile değiştirdi ve daha düşük maliyetle CLIP'i geçti. Bu ders InfoNCE'den sigmoid çiftli kayba (sigmoid pairwise loss) kadar matematiği inceler ve stdlib Python'da eğitim adımını uygular.

**Tür:** İnşa Et
**Diller:** Python (stdlib, InfoNCE + sigmoid kayıp uygulamaları)
**Önkoşullar:** Faz 12 · 01 (ViT yamaları), Faz 7 (Transformer'lar)
**Süre:** ~180 dakika

## Öğrenme Hedefleri

- Karşılıklı bilgiden (mutual information) InfoNCE kaybını türetme ve sayısal kararlı vektörel bir versiyon uygulama.
- Neden sigmoid çiftli kaybın (SigLIP) softmax'in gerektirdiği all-gather overhead'i olmadan 32768+ toplu iş boyutuna (batch size) kadar ölçeklendiğini açıklama.
- Metin şablonları (ör. `bir fotoğrafı {sınıf}`) oluşturarak ve kosinüs benzerliği (cosine similarity) üzerinde argmax alarak zero-shot ImageNet sınıflandırması çalıştırma.
- CLIP / SigLIP ön-eğitiminin verdiği dört kaldıracı adlandırma: toplu iş boyutu, sıcaklık (temperature), istem şablonu (prompt template), veri kalitesi.

## Sorun

CLIP öncesi görüntü işleri denetimliydi. Etiketli veri setleri toplanır (ImageNet: 1.2M görüntü, 1000 sınıf), bir CNN eğitilir, dağıtılır. Etiketler pahalıdır, etiketleyicilerin üzerinde anlaşabildiklerine eğilimlidir ve ince ayar yapılmadan yeni görevlere aktarılamaz.

Görüntü-açıklama web'inde bir milyarın üzerinde gevşek etiketli çift ücretsiz olarak mevcuttur. Alt metni "köpeğim Max parkta" olan altın retriever fotoğrafı bir denetim sinyali taşır — metin görüntüyü tarif eder. Soru: bunu kullanışlı eğitime dönüştürebilir misiniz?

CLIP'in cevabı: görüntü-açıklama çiftlerini bir eşleştirme görevi olarak ele almak. N görüntü ve N açıklama içeren bir toplu işte, her görüntüyü kendi açıklamasıyla N-1 dikkat dağıtıcıya (distractor) karşı eşleştirmeyi öğrenin. Denetim "bu iki şey birbirine ait; bu N-1 ait değil" şeklindedir. Sınıf etiketi yok. İnsan etiketlemesi yok. Sadece bir karşıtlık kaybı.

Elde edilen gömme uzayı CLIP'in eğitildiğinden fazlasını yapar. ImageNet zero-shot çalışır çünkü "bir kedinin fotoğrafı" hiç kedi olarak etiketlenmemiş kedi fotoğraflarının yakınına gömülür. Bu bahis, 2026'nın her VLM'ini doğurdu.

## Kavram

### Çift kodlayıcı (dual encoder)

CLIP'in iki kulesi vardır:

- Görüntü kodlayıcısı `f`: ViT veya ResNet, görüntü başına D boyutlu bir vektör çıkarır.
- Metin kodlayıcısı `g`: küçük bir transformer, açıklama başına D boyutlu bir vektör çıkarır.

Her iki kule de çıktılarını birim uzunluğa normalleştirir. Benzerlik `cos(f(x), g(y)) = f(x)^T g(y)`'dir çünkü her ikisi de birim normludur.

N (görüntü, açıklama) çiftinden oluşan bir toplu iş için `(N, N)` boyutunda benzerlik matrisi `S` oluşturun:

```
S[i, j] = cos(f(x_i), g(y_j)) / tau
```

#### Açıklama
Burada `tau` öğrenilen bir sıcaklıktır (CLIP 0.07 ile başlatır; log-uzayında öğrenilir).

### InfoNCE kaybı

CLIP, satırlar ve sütunlar üzerinde simetrik bir çapraz entropi (cross-entropy) kullanır:

```
loss_i2t = CE(S, labels=identity)     # her görüntünün pozitifi kendi açıklamasıdır
loss_t2i = CE(S^T, labels=identity)   # her açıklamanın pozitifi kendi görüntüsüdür
loss = (loss_i2t + loss_t2i) / 2
```

#### Açıklama
Bu InfoNCE'dir. CE'deki softmax, her görüntünün toplu işteki diğer tüm açıklamalardan ziyade kendi açıklamasıyla eşleşmesini zorlar. "Negatifler" toplu işteki diğer tüm öğelerdir. Daha büyük toplu işler = daha fazla negatif = daha güçlü sinyal. CLIP 32k toplu iş boyutuyla eğitildi; ölçek önemlidir.

### Sıcaklık (temperature)

`tau`, softmax'in keskinliğini (sharpness) kontrol eder. Düşük tau → keskin dağılım, sert negatif çıkarma (hard negative mining) etkisi. Yüksek tau → yumuşak, tüm örnekler katkıda bulunur. CLIP `log(1/tau)`'yu öğrenir, çöküşü önlemek için kırpılır (clip). SigLIP 2 başlangıçtau'sunu sabitler ve bunun yerine öğrenilen bir sapma (bias) kullanır.

### Neden sigmoid daha iyi ölçeklenir (SigLIP)

Softmax tüm benzerlik matrisinin senkronize olmasını gerektirir. Dağıtılmış eğitimde her gömmeyi (embedding) her yedek kopyaya (replica) all-gather yapmanız, ardından softmax'i çalıştırmanız gerekir. Bu iletişim için dünya boyutuna (world size) kareseldir.

SigLIP, softmax'i eleman bazlı sigmoid ile değiştirir: her `(i, j)` çifti için kayıp, " bunlar eşleşen çift mi?" ikili sınıflandırmasıdır. Pozitif sınıf etiketleri köşegen (diagonal) üzerindedir, diğer her şey negatiftir. Kayıp:

```
L = -1/N sum over (i, j) [ y_ij log sigmoid(S[i,j]) + (1-y_ij) log sigmoid(-S[i,j]) ]
```

#### Açıklama
`y_ij = 1` eğer `i == j`, aksi halde 0. Her çiftin kayıbı bağımsızdır. All-gather gerekmez. Her GPU kendi yerel bloğunu hesaplar ve toplar. SigLIP 2, CLIP'in orantılı olarak daha fazla iletişim gerektireceği yerde 32k-512k toplu iş boyutuna kadar ucuza ölçeklenir.

### Zero-shot sınıflandırma

N sınıf adı verildiğinde, her sınıf için bir metin şablonu oluşturun:

```
"bir fotoğrafı {sınıf}"
```

Her şablonu metin kodlayıcısıyla gömün. Görüntünüzü görüntü kodlayıcısıyla gömün. Kosinüs benzerliğinin argmax'ı = tahmini sınıf. Hedef sınıflarda eğitim yok.

İstem şablonları önemlidir. CLIP'in orijinal makalesi sınıfa 80 şablon kullandı (düz, sanatsal, fotoğraf, tablo vb.) ve gömmelerin ortalamasını aldı. +3 ImageNet puanı. Modern kullanımda genellikle bir veya iki şablon seçilir.

### Doğrusal prob (linear probe) ve ince ayar

Zero-shot bir temel ölçüttür. Donmuş CLIP özellikleri üzerinde tek bir doğrusal katman eğiterek hedef sınıflara uygulanan doğrusal prob, alan-içi görevlerde zero-shot'ı yener. Tam ince ayar, alan-içi görevlerde doğrusal prob'ı yener ama zero-shot transferi zedeleyebilir. Üç farklı rejim ve üç farklı uzlaşma.

### SigLIP 2: NaFlex ve yoğun özellikler

SigLIP 2 (2025) şunları ekler:
- NaFlex: tek model değişken en boy oranlarını ve çözünürlükleri işler.
- Segmentasyon ve derinlik tahmini için daha iyi yoğun özellikler, VLM'lerde donmuş omurga olarak kullanılmak üzere hedeflenir.
- Çok dilli: CLIP yalnızca İngilizce iken 100+ dilde eğitilmiştir.
- CLIP'in 400M'de kaldığı yerde 1B parametre ölçeği.

2026 açık VLM'lerinde SigLIP 2 SO400m/14 varsayılan görüntü kulesidir. CLIP, LAION-2B eğitim dağılımının sorgulama kalıbınızla eşleştiği saf görüntü-metin geri çağırma için hâlâ varsayılandır.

### ALIGN, BASIC, OpenCLIP, EVA-CLIP

ALIGN (Google, 2021): CLIP ile aynı fikir, 1.8B çift ölçeği, %90 gürültülü. Gürültülü verinin ölçeklendiğini kanıtladı. OpenCLIP (LAION): LAION-400M / 2B üzerinde CLIP'in açık yeniden üretimi, çoklu ölçekler, giden açık kontrol noktası. EVA-CLIP: maskeli görüntü modellemesinden başlatır; VLM'ler için güçlü omurga. BASIC: Google'ın CLIP+ALIGN melezi. Hepsi aynı aile, farklı veri ve ayar.

### Zero-shot tavanı

CLIP sınıfı modeller ImageNet zero-shot'ta yaklaşık %76'da tavan yapar (CLIP-G, OpenCLIP-G). Ötesi ya çok daha büyük veri gerektirir (SigLIP 2 %80+'a ulaşır) ya da mimari değişiklikler (denetimli kafalar, daha fazla parametre). Kıyaslama doygunlaşıyor; gerçek değer alt VLM'lerin tükettiği gömme uzayıdır.

## Kullan

`code/main.py` şunları uygular:

1. Hash tabanlı görüntü özellikleri ve metin karakter özellikleriyle çalışan oyuncu bir çift kodlayıcı, böylece numpy olmadan InfoNCE biçimini görebilirsiniz.
2. Saf Python'da InfoNCE kaybı (log-sum-exp ile sayısal kararlılık).
3. Karşılaştırma için sigmoid çiftli kayıp.
4. Zero-shot sınıflandırma rutini: bir metin istemi kümesine karşı kosinüs benzerliği hesaplama, argmax ile tahmin.

Çalıştırın ve kayıp eğrisini izleyin. Mutlak değerler oyuncudur; biçim gerçek bir CLIP eğitimcisinden çıkanla eşleşir.

## Teslimat

Bu ders `outputs/skill-clip-zero-shot.md` dosyasını üretir. Bir görüntü kümesi (yol üzerinden) ve hedef sınıflar listesi verildiğinde, CLIP şablonuyla metin istemleri oluşturur, her iki tarafı belirtilen bir kontrol noktası (ör. `openai/clip-vit-large-patch14`) ile gömer ve benzerlik puanlarıyla birlikte üst-1 / üst-5 tahminlerini döndürür. Beceri, istem listesinde olmayan sınıflar hakkında iddia yapmayı reddeder.

## Alıştırmalar

1. 4 çiftlik bir toplu iş için InfoNCE'yi elle uygulayın. 4x4 benzerlik matrisini oluşturun, softmax'i çalıştırın, köşegeni seçin, çapraz entropiyi hesaplayın. Python uygulamanızı bu el hesaplamasıyla doğrulayın.

2. SigLIP, sıcaklığa ek olarak bir `b` sapma parametresi kullanır: `S'[i,j] = S[i,j]/tau + b`. Toplu işte büyük bir sınıf dengesizliği (satır başına negatiflerin pozitiflerden çok daha fazla olduğu) olduğunda `b`'nin rolü nedir? SigLIP Bölüm 3'ü okuyun (arXiv:2303.15343).

3. Kedi ve köpek için bir zero-shot sınıflandırıcı oluşturun. İki istem şablonu deneyin: `bir fotoğrafı {sınıf}` ve `bir resmi {sınıf}`. 100 test görüntüsü üzerinde doğruluğu ölçün. Şablonların ensamblesi (ensemble) tekliyi yener mi?

4. 512 GPU ile 32k toplu iş boyutunda softmax InfoNCE vs sigmoid çiftli için iletişim maliyetini hesaplayın. Hangisi O(N) ile, hangisi O(N^2) ile ölçeklenir? SigLIP Bölüm 4'e atıfta bulunun.

5. OpenCLIP ölçekleme yasaları makalesini okuyun (arXiv:2212.07143, Cherti ve diğerleri). Şekillerden veri ölçeklemesi için sonuçlarını yeniden üretin: sabit model boyutunda, ImageNet zero-shot doğruluğu ile eğitim verisi boyutu arasındaki log-doğrusal ilişki nedir?

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| InfoNCE | "Karşıtlık kaybı" | Bir toplu işin benzerlik matrisi üzerinde çapraz entropi; her öğenin pozitifi eşleşen çiftidir, negatifler diğer her şeydir |
| Sigmoid kaybı | "SigLIP kaybı" | Çift bazlı ikili çapraz entropi; softmax yok, all-gather yok, dağıtılmış eğitimde ucuza ölçeklenir |
| Sıcaklık (Temperature) | "tau" | Softmax/sigmoid öncesi logit'leri ölçekleyen skaler; dağılımın keskinliğini kontrol eder |
| Zero-shot | "İnce ayarsız sınıflandırma" | Sınıf gömmeleri oluşturmak için metin istemleri kullanma ve kosinüs benzerliğiyle sınıflandırma; hedef sınıflarda eğitim yok |
| İstem şablonu (Prompt template) | "bir fotoğrafı ..." | Sınıf adı etrafındaki metin iskeleti; zero-shot doğruluğunu 1-5 puan etkiler |
| Çift kodlayıcı (Dual encoder) | "İkili kule" | Bir görüntü kodlayıcısı + bir metin kodlayıcısı, paylaşılı D boyutlu uzayda çıktılar |
| Sert negatif (Hard negative) | "Zorlayıcı dağıtıcı" | Pozitife kadar yeterince benzer olan negatif; modelin onları ayırması gerekir |
| Doğrusal prob (Linear probe) | "Donmuş + tek katman" | Donmuş özelliklerin yalnızca bir doğrusal sınıflandırıcısını eğitme; özellik kalitesini ölçer |
| NaFlex | "Yerel esnek çözünürlük" | SigLIP 2'nin yeniden boyutlandırma olmadan her en boy oranında görüntüleri işleme yeteneği |
| Sıcaklık ölçeklemesi | "log-parametrize edilmiş tau" | CLIP `log(1/tau)`'yu parametrize eder; gradyanların düzgün çalışmasını sağlar; neredeyse sıfıra düşmeyi önler |

## İleri Okuma

- [Radford ve diğerleri — Doğal Dil Gözetiminden Öğrenilebilir Görüntü Modelleri (arXiv:2103.00020)](https://arxiv.org/abs/2103.00020) — CLIP makalesi.
- [Zhai ve diğerleri — Dil-Görüntü Ön-Eğitimi için Sigmoid Kaybı (arXiv:2303.15343)](https://arxiv.org/abs/2303.15343) — SigLIP.
- [Tschannen ve diğerleri — SigLIP 2 (arXiv:2502.14786)](https://arxiv.org/abs/2502.14786) — çok dilli + NaFlex.
- [Jia ve diğerleri — ALIGN (arXiv:2102.05918)](https://arxiv.org/abs/2102.05918) — gürültülü web verisiyle ölçek.
- [Cherti ve diğerleri — Karşıtlıklı dil-görüntü öğrenmesinin tekrarlanabilir ölçekleme yasaları (arXiv:2212.07143)](https://arxiv.org/abs/2212.07143) — OpenCLIP ölçekleme yasaları.
