# Diffusion Modelleri — Sıfırdan DDPM

> Ho, Jain, Abbeel (2020) alana bırakılamayacak bir tarif verdi. Veriyi bin küçük adımda gürültüyle yok edin. Bir sinir ağı eğiterek gürültüyü tahmin edin. Inference'ta işlemi tersine çevirin. Bugün her ana akım görüntü, video, 3D ve müzik modeli bu döngü üzerinde çalışıyor, muhtemelen üzerine flow matching veya consistency hileleri eklenmiş olarak.

**Tür:** Oluşturma
**Diller:** Python
**Önkoşullar:** Faz 3 · 02 (Backprop), Faz 8 · 02 (VAE)
**Süre:** ~75 dakika

## Problem

`p_data(x)` için bir örnekleyici istiyorsunuz. GAN'lar genellikle sapmaya başlayan bir minimax oyunu oynar. VAE'ler Gauss decoder'dan bulanık örnekler üretir. Aslında istediğiniz şey (a) tek bir stabil kayıp (değil nokta, minimax yok), (b) `log p(x)` üzerinde bir alt sınır (yani likelihood'larınız var) ve (c) SOTA kalitesine eşdeğer örnekler sağlayan bir eğitim hedefidir.

Sohl-Dickstein et al. (2015) teorik bir cevabı vardı: yavaş yavaş Gauss gürültüsü ekleyen bir Markov zinciri `q(x_t | x_{t-1})` tanımlayın ve denoisying yapan ters bir zincir `p_θ(x_{t-1} | x_t)` eğitin. Ho, Jain, Abbeel (2020) kaybın tek bir satıra indirgenebileceğini gösterdi — gürültüyü tahmin edin — ve matematikleri temizledi. 2020'de bu bir meraktı. 2021'de en iyi durumdaki örnekleri üretti. 2022'de Stable Diffusion haline geldi. 2026'da ise temel yapı taşdır.

## Kavram

![DDPM: ileri gürültü, ters denoising](../assets/ddpm.svg)

**İleri süreç `q`.** `T` küçük adımda Gauss gürültüsü ekleyin. Kapalı form — matematiğin işlenebilir olmasının nedeni — birikimli adımın da Gauss olmasıdır:

```
q(x_t | x_0) = N( sqrt(α̅_t) · x_0,  (1 - α̅_t) · I )
```

#### Açıklama
Burada `α̅_t = ∏_{s=1..t} (1 - β_s)`, `β_t` programı içindir. T=1000 adım boyunca 1e-4'ten 0.02'ye doğru lineer `β_t` seçin ve `x_T` yaklaşık olarak `N(0, I)` olur.

**Ters süreç `p_θ`.** Eklenen gürültüyü tahmin eden bir sinir ağı `ε_θ(x_t, t)` öğrenin. Verilen `x_t` ile denoising:

```
x_{t-1} = (1 / sqrt(α_t)) · ( x_t - (β_t / sqrt(1 - α̅_t)) · ε_θ(x_t, t) )  +  σ_t · z
```

#### Açıklama
Burada `σ_t` ya `sqrt(β_t)` ya da öğrenilmiş bir varyanstır. İfade çirkin ama sadece cebirdir — `q(x_{t-1} | x_t, x_0)` posteriöründen `x_{t-1}`'i çözmek ve `x_0`'ı gürültü-tahmini tahminiyle değiştirmektir.

**Eğitim kaybı.**

```
L_simple = E_{x_0, t, ε} [ || ε - ε_θ( sqrt(α̅_t) · x_0 + sqrt(1 - α̅_t) · ε,  t ) ||² ]
```

#### Açıklama
Veriden `x_0` örnekle, rastgele bir `t` seç, `ε ~ N(0, I)` örnekle, kapalı formu tek seferde kullanarak gürültülü `x_t`'yi hesapla ve gürültü üzerinde regresyon yap. Tek kayıp, minimax yok, KL yok, reparameterization hilesi yok.

**Örnek alma.** `x_T ~ N(0, I)` ile başla. `t = T`'den `1`'e kadar ters adımı tekrarla. Bitti.

## Neden çalışır

Üç sezgi:

1. **Denoising kolaydır; üretmek zordur.** `t=T`'de veri saf gürültüdür — ağ önemsiz bir sorunu çözmek zorundadır. `t=0`'da ağ sadece birkaç pikseli temizlemelidir. Ara `t`'de sorun zordur ama ağa her gürültü seviyesinden aynı ağırlıklardan akan birçok gradyan vardır.

2. **Kostüm giydirilmiş skor eşleme.** Vincent (2011), gürültüyü tahmin etmenin `∇_x log q(x_t | x_0)` — *skor* — tahmin etmeye eşdeğer olduğunu kanıtladı. Ters SDE bu skoru yoğunluk gradyanı boyunca yürütmek için kullanır — yüksek olasılıklı bölgelere doğru yönlendirilmiş rastgele bir yürüyüş.

3. **ELBO basit MSE'ye dönüşür.** Tam varyasyonel alt sınırda zaman adımı başına bir KL terimi vardır. DDPM'nin parametrelendirmesiyle bu KL terimleri, belirli katsayılara sahip gürültü tahmininde MSE'ye basitleşir; Ho katsayıları attı (buna "basit" kayıp dedi) ve kalite *iyileşti*.

## Kodu Oluştur

`code/main.py`, 1 boyutlu bir DDPM uygular. Veri iki modlu bir karışımdir. "Ağ", `(x_t, t)` alan ve tahmini gürültüyü çıktı veren küçük bir MLP'dir. Eğitim tek satırlık kayıptır. Örnek alma ters zinciri tekrarlar.

### Adım 1: ileri program (kapalı form)

```python
betas = [1e-4 + (0.02 - 1e-4) * t / (T - 1) for t in range(T)]
alphas = [1 - b for b in betas]
alpha_bars = []
cum = 1.0
for a in alphas:
    cum *= a
    alpha_bars.append(cum)
```

#### Açıklama
Lineer beta programı, her adımda ne kadar gürültü ekleneceğini belirler.

### Adım 2: `x_t`'yi tek seferde örnekle

```python
def forward_sample(x0, t, alpha_bars, rng):
    a_bar = alpha_bars[t]
    eps = rng.gauss(0, 1)
    x_t = math.sqrt(a_bar) * x0 + math.sqrt(1 - a_bar) * eps
    return x_t, eps
```

#### Açıklama
Kapalı form sayesinde herhangi bir zaman adımındaki gürültülü örneği doğrudan üretebiliriz.

### Adım 3: bir eğitim adımı

```python
def train_step(x0, model, alpha_bars, rng):
    t = rng.randrange(T)
    x_t, eps = forward_sample(x0, t, alpha_bars, rng)
    eps_hat = model_forward(model, x_t, t)
    loss = (eps - eps_hat) ** 2
    return loss, gradient_step(model, ...)
```

#### Açıklama
Modelin gürültü tahmini ile gerçek gürültü arasındaki kare fark kayıptır.

### Adım 4: ters örnek alma

```python
def sample(model, alpha_bars, T, rng):
    x = rng.gauss(0, 1)
    for t in range(T - 1, -1, -1):
        eps_hat = model_forward(model, x, t)
        beta_t = 1 - alphas[t]
        x = (x - beta_t / math.sqrt(1 - alpha_bars[t]) * eps_hat) / math.sqrt(alphas[t])
        if t > 0:
            x += math.sqrt(beta_t) * rng.gauss(0, 1)
    return x
```

#### Açıklama
40 zaman adımı ve 24 birimlik MLP ile 1 boyutlu bir problemde, bu iki modlu karışımı yaklaşık 200 epoch'ta öğrenir.

## Zaman koşullandırması

Ağın hangi zaman adımında denoising yaptığını bilmesi gerekir. İki standart seçenek:

- **Sinüzoit embedding.** Transformer konumsal kodlaması gibi. `embed(t) = [sin(t/ω_0), cos(t/ω_0), sin(t/ω_1), ...]`. MLP'den geçirin, ağa yayınlayın.
- **FiLM / group-norm koşullandırması.** Embedding'i her blokta kanal başına ölçek/kaydırma (FiLM) olarak uygulayın.

Oyuncak kodumuz sinüzoit → concat kullanır. Üretim U-Net'leri FiLM kullanır.

## Tuzaklar

- **Program çok önemlidir.** Lineer `β` DDPM varsayılanıdır ama kosinüs programı (Nichol & Dhariwal, 2021) aynı hesaplama için daha iyi FID verir. Kalite plato yaparsa programı değiştirin.
- **Zaman adımı embedding'i kırılgandır.** Ham `t`'yi float olarak geçmek oyuncak 1 boyutlu için çalışır ama görüntüler için başarısız olur; her zaman uygun bir embedding kullanın.
- **V-tahmini vs ε-tahmini.** Dar rejimlerde (çok küçük veya çok büyük t), `ε`'nin sinyal-gürültü oranı düşüktür. V-tahmini (`v = α·ε - σ·x`) daha stabildir; SDXL, SD3 ve Flux bunu kullanır.
- **Classifier-free guidance.** Inference'ta hem koşullu hem de koşulsuz `ε` hesaplayın, ardından `ε_cfg = (1 + w) · ε_cond - w · ε_uncond` ile `w ≈ 3-7`. Ders 08'de ele alınır.
- **1000 adım çok fazladır.** Üretim DDIM (20-50 adım), DPM-Solver (10-20 adım) veya distilasyon (1-4 adım) kullanır. Ders 12'ye bakın.

## Kullan

| Rol | 2026'da tipik yığın |
|------|-----------------------|
| Görüntü piksel alanı diffusion (küçük, oyuncak) | DDPM + U-Net |
| Görüntü latent diffusion | VAE encoder + U-Net veya DiT (Ders 07) |
| Video latent diffusion | Zamansal-mekansal DiT (Sora, Veo, WAN) |
| Ses latent diffusion | Encodec + diffusion transformer |
| Bilim (moleküller, proteinler, fizik) | Eşdeğer diffusion (EDM, RFdiffusion, AlphaFold3) |

Diffusion evrensel generatif omurgadır. Flow matching (Ders 13), aynı kalite için inference hızında genellikle kazanan 2024-2026 rakibidir.

## Sun

`outputs/skill-diffusion-trainer.md` olarak kaydedin. Beceri bir veri seti + hesaplama bütçesi alır ve çıktıyı verir: program (lineer/kosinüs/sigmoid), tahmin hedefi (ε/v/x), adım sayısı, rehberlik ölçeği, örnekleyici ailesi ve bir değerlendirme protokolü.

## Alıştırmalar

1. **Kolay.** `code/main.py` dosyasında T'yi 40'tan 10'a değiştirin. Örnek kalitesi (çıktıların görsel histogramı) nasıl bozulur? İki modlu yapı hangi T'de çöker?
2. **Orta.** ε-tahmininden v-tahminine geçin. Ters adımı yeniden türetin. Son örnek kalitesini karşılaştırın.
3. **Zor.** Classifier-free guidance ekleyin. Bir sınıf etiketi `c ∈ {0, 1}` ile koşullandırın, eğitim sırasında %10 düşürün ve örnekleme zamanında `ε = (1+w)·ε_cond - w·ε_uncond` kullanın. `w = 0, 1, 3, 7`'de koşullu mod-isabet oranını ölçün.

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|------|-----------------|-----------------------|
| Forward process (İleri süreç) | "Gürültü ekleme" | Veriyi yok eden sabit Markov zinciri `q(x_t \| x_{t-1})`. |
| Reverse process (Ters süreç) | "Denoising" | Veriyi yeniden oluşturan öğrenilmiş zincir `p_θ(x_{t-1} \| x_t)`. |
| β schedule (β programı) | "Gürültü merdiveni" | Adım başına varyans; lineer, kosinüs veya sigmoid. |
| α̅ | "Alpha bar" | Birikimli çarpım `∏(1 - β)`; `x_0`'dan kapalı formda `x_t` verir. |
| Simple loss (Basit kayıp) | "Gürültü üzerinde MSE" | `\|\|ε - ε_θ(x_t, t)\|\|²`; tüm varyasyonel türetmeler buna dönüşür. |
| ε-prediction (ε-tahmini) | "Gürültüyü tahmin et" | Çıktı eklenen gürültüdür; standart DDPM. |
| V-prediction (V-tahmini) | "Hızı tahmin et" | Çıktı `α·ε - σ·x`'tir; t boyunca daha iyi koşullandırma. |
| DDPM | "Makale" | Ho et al. 2020; lineer β, 1000 adım, U-Net. |
| DDIM | "Deterministik örnekleyici" | Markov olmayan örnekleyici, 20-50 adım, aynı eğitim hedefi. |
| Classifier-free guidance | "CFG" | Koşullu ve koşulsuz gürültü tahminlerini karıştırarak koşul güçlendirmesi. |

## Üretim notu: diffusion inference bir adım-sayısı sorunudur

DDPM makalesi T=1000 ters adım çalıştırır. Bunu üretimde kimse sunmaz. Her gerçek inference yığını üç stratejiden birini seçer — ve her biri üretimin "gecikme nereden geliyor" çerçevesine temiz bir şekilde karşılık gelir:

1. **Daha hızlı örnekleyici, aynı model.** DDIM (20-50 adım), DPM-Solver++ (10-20), UniPC (8-16). Ters döngünün drop-in değiştirilmesi; eğitilmiş `ε_θ` ağırlıklarına dokunulmaz. Gecikmeyi 20-50x azaltır.
2. **Distilasyon.** Bir öğrenciyi daha az adımda öğretmenle eşleşecek şekilde eğitin: Progressive Distillation (2 → 1), Consistency Models (keyfi → 1-4), LCM, SDXL-Turbo, SD3-Turbo. Gecikmeyi başka bir 5-10x azaltır, yeniden eğitim gerektirir.
3. **Önbellekleme ve derleme.** `torch.compile(unet, mode="reduce-overhead")`, TensorRT-LLM diffusion arka uçları, `xformers`/SDPA attention, bf16 ağırlıkları. Adım başına gecikmeyi ~2x azaltır. (1) ve (2) ile istiflenir.

Bir üretim diffusion sunucusu için bütçe konuşması, production literatürünün LLM'ler için tarif ettiğiyle aynıdır: gecikme `adım_sayısı × adım_maliyeti + VAE_decode`'dur, verimlilik `toplu_boyutu × (adım_sayısı × adım_maliyeti)^-1`'dir. TTFT küçüktür (bir adım); TPOT-eşdeğeri tam yanıt süresidir çünkü görüntü üretimi kullanıcı perspektifinden "hepsi bir arada" gerçekleşir.

## Daha Fazla Kaynak

- [Sohl-Dickstein et al. (2015). Deep Unsupervised Learning using Nonequilibrium Thermodynamics](https://arxiv.org/abs/1503.03585) — diffusion makalesi, zamanının önünde.
- [Ho, Jain, Abbeel (2020). Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239) — DDPM.
- [Song, Meng, Ermon (2021). Denoising Diffusion Implicit Models](https://arxiv.org/abs/2010.02502) — DDIM, daha az adım.
- [Nichol & Dhariwal (2021). Improved DDPM](https://arxiv.org/abs/2102.09672) — kosinüs programı, öğrenilmiş varyans.
- [Dhariwal & Nichol (2021). Diffusion Models Beat GANs on Image Synthesis](https://arxiv.org/abs/2105.05233) — classifier guidance.
- [Ho & Salimans (2022). Classifier-Free Diffusion Guidance](https://arxiv.org/abs/2207.12598) — CFG.
- [Karras et al. (2022). Elucidating the Design Space of Diffusion-Based Generative Models (EDM)](https://arxiv.org/abs/2206.00364) — birleşik gösterim, en temiz tarif.
