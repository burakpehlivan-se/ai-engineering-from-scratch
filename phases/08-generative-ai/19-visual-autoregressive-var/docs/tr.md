# Visual Autoregressive Modeling (VAR): Next-Scale Prediction

> Diffüzyon modelleri zamanda yinelemeli olarak örnekleme yapar (gürültü temizleme adımları). VAR ise ölçek (scale) bakımından yinelemeli örnekleme yapar — 1x1 bir token tahmin eder, sonra 2x2, sonra 4x4, son çözünürlüğe kadar; her ölçek bir öncekine koşullandırılır. 2024 makalesi, VAR'ın görsel üretimi için GPT tarzı ölçekleme yasalarını (scaling laws) takip ettiğini ve aynı hesaplama bütçesinde DiT'i yendiğini gösterdi. Bu ders temel mekanizmayı inşa eder.

**Tür:** İnşa Et
**Diller:** Python (PyTorch ile)
**Ön koşullar:** Faz 7 Ders 03 (Multi-Head Attention), Faz 8 Ders 06 (DDPM)
**Süre:** ~90 dakika

## Problem

Otogresif (autoregressive) üretim, dil modellemesine egemen oldu çünkü öngörülebilir biçimde ölçeklenir: daha fazla hesaplama, daha fazla parametre, daha düşük perplexity, daha iyi çıktılar. Görsel üretimi, 2024 öncesinde iki ana AR denemesi yaşadı: PixelRNN/PixelCNN (piksel piksel) ve DALL-E 1 / Parti / MuseGAN (VQ-VAE kodlarında token token).

Her ikisi de üretim sırası sorunundan mustarip. Pikseller ve token'lar 2D bir ızgarada düzenlenir, ancak AR modelinin bunları 1D raster sırasıyla ziyaret etmesi gerekir. Erken bir köşe pikselinin görselin sonunda neye dönüşeceği hakkında hiçbir fikri yoktur. Üretim kalitesi GPT-metin üzerindekinden daha kötü ölçeklendi ve eşleşen hesaplamada diffüzyon modeli kalitesine hiçbir zaman ulaşamadı.

VAR, neyin üretildiğini değiştirerek üretim sırası sorununu çözer. Görsel token'larını uzayda tek tek tahmin etmek yerine, VAR artan çözünürlüklerde tüm bir görseli tahmin eder. Adım 1: 1x1 bir token tahmin et (genel görsel "özeti"). Adım 2: 2x2 bir ızgara token tahmin et (daha kaba özellikler). Adım 3: 4x4 bir ızgara tahmin et. Adım K: son (H/8)x(W/8) ızgarayı tahmin et.

Her ölçek, önceki tüm ölçekleri (ölçek sırası bakımından nedensel olarak) ve kendi ölçeği içinde paralel olarak dikkate alır. Sıra sorunu kaybolur: k ölçeğindeki tüm görsel bir transformer geçişinde üretilir.

## Kavram

### VQ-VAE Çoklu Ölçekli Tokenizer

VAR, **çoklu ölçekli ayrık (discrete) bir tokenizer** gerektirir. Bir görsel x için, giderek daha yüksek çözünürlüklü token ızgaraları dizisi üretir:

```
x -> encoder -> latent f
f -> tokenize at 1x1: token grid z_1 of shape (1, 1)
f -> tokenize at 2x2: token grid z_2 of shape (2, 2)
...
f -> tokenize at (H/p)x(W/p): token grid z_K of shape (H/p, W/p)
```

Her z_k aynı sözlüğü (codebook) kullanır (tipik boyut 4096-16384). Her ölçekteki tokenizasyon bağımsız değildir — her ölçekteki artık değerleri (residuals) topladığınızda f'yi yeniden oluşturacak şekilde eğitilmiştir:

```
f ≈ upsample(embed(z_1), target_size) + ... + upsample(embed(z_K), target_size)
```

Bu bir **artımlı VQ** (residual VQ) varyantıdır. Ölçek k, 1..k-1 ölçeklerinin kaçırdıklarını yakalar. Decoder tüm ölçek embedding'lerinin toplamını alır ve görseli üretir.

Çoklu ölçekli VQ tokenizer bir kez eğitilir (VQGAN gibi) ve sonra dondurulur. Tüm üretici çalışma, üzerindeki otogresif modele aittir.

### Next-Scale Prediction (Sonraki Ölçek Tahmini)

Üretici model, önceki tüm ölçeklerden token'ları gören ve bir sonraki ölçekteki token'ları tahmin eden bir transformer'dır.

Girdi dizi yapısı:
```
[START, z_1 tokens, z_2 tokens, z_3 tokens, ..., z_K tokens]
```

Konumsal embedding'ler hem ölçekteki dizin indeksini hem de ölçek içindeki uzamsal konumu kodlar. Attention, ölçek sırası bakımından nedenseldir: k ölçüğündeki (i, j) konumundaki token, 1..k ölçeklerindeki tüm token'lara ve k ölçeğinde intra-ölçek sırası ne olursa olsun daha önce gelen token'lara dikkat edebilir (VAR, intra-ölçek nedenselliği olmadan sabit konumsal attention kullanır — bir ölçek içindeki tüm konumlar paralel olarak tahmin edilir).

Eğitim kaybı: her ölçekte k, önceki ölçek token'ları verildiğinde token'ları z_k tahmin etme. Ayrık VQ kodlarında çapraz entropy kaybı. GPT ile aynı yapı, ancak "dizi" artık ölçek-yapılandırılmış.

### Üretim

Çıkarımda:
```
generate z_1 = sample from p(z_1)                    # 1 token
generate z_2 = sample from p(z_2 | z_1)              # 4 tokens in parallel
generate z_3 = sample from p(z_3 | z_1, z_2)         # 16 tokens in parallel
...
decode: f = sum of embed-and-upsample scales 1..K
image = VAE_decoder(f)
```

K = 10 ölçek için üretim, 10 transformer ileri geçişi demektir. Her geçiş kendi tüm ölçeğini paralel olarak üretir — bir ölçek içinde token bazında otoregresiflik yoktur. 256x256 bir görsel için bu, DiT'in 28-50'sine kıyasla yaklaşık 10 geçiştir.

### Neden Next-Scale, Next-Token'i Yener

Üç yapısal avantaj:
1. **Kaba-ince doğal görsel istatistikleriyle hizalıdır.** İnsan algısı ve görsel veri setleri her ikisi de ölçeğe bağlı düzenlilikler (regularities) sergiler: düşük frekans yapı kararlı ve öngörülebilirdir; yüksek frekans detay düşük frekans içeriğine koşulludur. Next-scale prediction bundan yararlanır.
2. **Ölçek içinde paralel üretim.** GPT tarzı token AR'dan farklı olarak, VAR bir ölçekteki tüm token'ları bir adımda üretir. Etkin üretim uzunluğu lineer yerine log-ölçeklidir.
3. **Üretim sırası yanlılığı yoktur.** k ölçüğündeki token'lar k-1 ölçüğünün tamamını görür; erken token'ların geç bağlamı kullanılamazken taahhütte bulunmasını zorlayan "solda" veya "yukarıda" yanlılığı yoktur.

### Ölçekleme Yasası (Scaling Law)

Tian ve ark., VAR'ın ImageNet üzerinde FID için bir kuvvet-yasası (power-law) ölçekleme eğrisini takip ettiğini gösterdi — tıpkı GPT'nin perplexity için yaptığı gibi. Parametreleri veya hesaplamayı iki katına çıkarmak hatayı güvenilir bir şekilde ikiye böler. Bu, dil modelleri kadar temiz bir şekilde bu tür davranış sergileyen ilk görüntü-üretici model oldu. Sonuç olarak, VAR ölçekli tahminler hesaplamadan öngörülebilir hale gelir, mimariye göre deneysel tahminler değil.

### Diffüzyonla İlişkisi

VAR ve diffüzyon aynı veri-sıkıştırma hikayesini paylaşır: her ikisi üretim sorununu bir dizi daha kolay alt-soruna böler.

- Diffüzyon: kademeli olarak gürültü ekleyin, bir adımı geri almayı öğrenin.
- VAR: kademeli olarak çözünürlük ekleyin, sonraki ölçüğü tahmin etmeyi öğrenin.

Sorunun farklı eksenleridir. Her ikisi de hesaplanabilir koşullu dağılımlar üretir. Deneysel olarak VAR çıkarımda daha hızlıdır (daha az geçiş, ölçek içinde paralel) ve sınıflı-koşullu ImageNet'te DiT ile eşleşir veya onu yener. Metin-koşullu VAR (VARclip, HART) aktif bir araştırma alanıdır.

## İnşa Et

`code/main.py`'de şunları yapacaksınız:
1. Sentetik "görsel" verileri (2D Gaussian halkaları) üzerinde küçük bir **çoklu ölçekli VQ tokenizer** oluşturun.
2. Token'ları next-scale tahmini yapacak **VAR tarzı bir transformer** eğitin.
3. Transformer'ı 4 kez çağırarak (4 ölçek) ve decode ederek örnekleme yapın.
4. Ölçek sıralı eğitimin, ölçek içinde paralel üretimi nasıl sağladığını doğrulayın.

Bu bir oyuncak uygulamadır. Nokta, ölçek-yapılandırılmış attention maskesinin ve ölçek-içi paralel üretimin gerçekten çalıştığını görmektir.

## Teslim Et

Bu ders `outputs/skill-var-tokenizer-designer.md` üretir — çoklu ölçekli tokenizer tasarlama becerisi: ölçek sayısı, ölçek oranları, sözlük boyutu, artık değer paylaşımı (residual sharing), decoder mimarisi.

## Alıştırmalar

1. **Ölçek sayısı ablatasyonu.** VAR'ı 4, 6, 8, 10 ölçekle eğitin. Yeniden oluşturma kalitesini otoregresif geçiş sayısına göre ölçün. Daha fazla ölçek = daha ince artık değerler = daha iyi kalite ama daha fazla geçiş.

2. **Sözlük boyutu.** 512, 4096, 16384 sözlük boyutlarıyla tokenizer'lar eğitin. Daha büyük sözlükler daha iyi yeniden oluşturma verir ama daha zor tahmin. Dirseği bulun.

3. **Ölçek-içi paralellik kontrolü.** Eğitilmiş bir VAR için attention kalıbını açıkça ölçün. k ölçüğünde model çapraz-ölçek konumlarına mı dikkat ediyor ama intra-ölçek konumlarına mı etmiyor? Mask uygulamasını doğrulayın.

4. **VAR vs DiT ölçekleme.** Aynı ImageNet sınıflı-koşullu görevi için, VAR ve DiT'i eşleşen parametre bütçelerinde eğitin (örn. 33M, 130M, 458M). FID vs hesaplamayı çizdirin. VAR her boyutta DiT'in önüne geçmeli — makalenin sonucunu küçük ölçekte yeniden üretin.

5. **Metin koşullandırması.** VAR'ı adaLN aracılığıyla bir metin embedding'i (CLIP pooled) ek koşullandırma girdisi olarak alacak şekilde genişletin. Bu HART reçetesidir. Metinle eşleşen örneklemede FID ne kadar iyileşir?

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| VAR | "Visual AutoRegressive" | VQ token ızgaraları piramidi üzerinde next-scale prediction ile görsel üretimi |
| Next-scale prediction | "Kaba tahmin et, sonra ince" | Model artan çözünürlük ölçeklerinde token'ları, önceki tüm ölçeklere koşullandırarak tahmin eder |
| Çoklu ölçekli VQ tokenizer | "Artımlı VQ" | Artan çözünürlükte K token ızgarası üreten ve decoder'ın tüm ölçekleri toplayan VQ-VAE |
| Ölçek k | "Piramit düzeyi k" | K çözünürlük düzeyinden biri, k=1'de 1x1'den k=K'de (H/p)x(W/p)'e |
| Ölçek-içi paralellik | "Ölçek başına tek geçiş" | k ölçüğündeki tüm token'lar bir transformer geçişinde tahmin edilir, otoregresif değil |
| Ölçekler arası nedensellik | "Ölçek sıralı attention" | k ölçüğündeki token 1..k ölçeklerinin tamamına dikkat edebilir ama k+1..K ölçeklerine edemez |
| Artımlı VQ | "Toplamalı tokenizasyon" | Her ölçüğün token'ları daha düşük ölçeklerin bıraktığı artık değeri kodlar; decoder tüm ölçek embedding'lerini toplar |
| VAR ölçekleme yasası | "ImageGPT ölçeklemesi" | FID, hesaplamada öngörülebilir bir kuvvet-yasası izler, dil modellerinin perplexity'si gibi |
| HART | "Hibrit VAR + metin" | MaskGIT tarzı yinelemeli decode'u VAR'ın ölçek yapısıyla birleştiren metin-koşullu VAR varyantı |
| Ölçek konumsal embedding | "(ölçek, satır, sütun) üçlüsü" | Konumsal kodlama hem ölçekteki dizin indeksini hem de ölçek içindeki uzamsal koordinatları taşır |

## Daha Fazla Kaynak

- [Tian ve ark., 2024 — "Visual Autoregressive Modeling: Scalable Image Generation via Next-Scale Prediction"](https://arxiv.org/abs/2404.02905) — VAR makalesi, kanonik referans
- [Peebles ve Xie, 2022 — "Scalable Diffusion Models with Transformers"](https://arxiv.org/abs/2212.09748) — DiT, diffüzyon karşılaştırma temel hattı
- [Esser ve ark., 2021 — "Taming Transformers for High-Resolution Image Synthesis"](https://arxiv.org/abs/2012.09841) — VQGAN, VAR'ın çoklu ölçekli tokenizer'ının genişlediği tokenizer ailesi
- [van den Oord ve ark., 2017 — "Neural Discrete Representation Learning"](https://arxiv.org/abs/1711.00937) — VQ-VAE, ayrık görsel tokenizasyonunun temeli
- [Tang ve ark., 2024 — "HART: Efficient Visual Generation with Hybrid Autoregressive Transformer"](https://arxiv.org/abs/2410.10812) — metin-koşullu VAR
