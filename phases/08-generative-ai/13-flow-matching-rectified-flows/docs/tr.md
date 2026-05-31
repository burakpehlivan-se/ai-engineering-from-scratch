# Flow Matching & Rectified Flows

> Diffüzyon modelleri, gürültüden veriye kavisli bir yolda yürüdükleri için 20-50 örnekleme adımı alır. Flow matching (Lipman ve ark., 2023) ve rectified flow (Liu ve ark., 2022) düz yollar eğitti. Daha düz yollar daha az adım demektir, daha az adım daha hızlı çıkarım demektir. Stable Diffusion 3, Flux.1 ve AudioCraft 2, 2024'te tümü flow matching'e geçti.

**Tür:** İnşa Et
**Diller:** Python
**Ön koşullar:** Faz 8 · 06 (DDPM), Faz 1 · Calculus
**Süre:** ~45 dakika

## Problem

DDPM'nin ters süreci, `N(0, I)`'den veri dağılımı geri dönen 1000 adımlık stokastik bir yürüyüşdür. DDIM bunu 20-50 deterministik adıma çökertti. Daha az adım istiyorsunuz — ideal olarak bir. Engel, ters çözümü çözen ODE'nin sert (stiff) olmasıdır; yol kavislidir.

Eğer modeli gürültüden veriye giden yolun *düz bir çizgi* olduğu şekilde eğitebilseydiniz, `t=1`'den `t=0`'a kadar tek bir Euler adımı işe yarardı. Flow matching bunu doğrudan inşa eder: `x_1 ∼ N(0, I)`'den `x_0 ∼ data`'ya düz çizgi interpolasyonu tanımlayın, zaman türevine eşleşen bir vektör alanı `v_θ(x, t)` eğitin, çıkarımda entegre edin.

Rectified flow (Liu 2022) daha da ileri gider: reflow prosedürüyle yolları yinelemeli olarak düzleştirir, giderek daha near-linear (doğrusala yakın) yaklaşan bir ODE üretir. İki reflow yinelemesinden sonra 2 adımlı örneleyici, 50 adımlık DDPM kalitesine eşit olur.

## Kavram

![Flow matching: gürültü ve veri arasında düz çizgi interpolasyonu](../assets/flow-matching.svg)

### Düz çizgi flow'u

Tanımlayın:

```
x_t = t · x_1 + (1 - t) · x_0,   t ∈ [0, 1]
```

#### Açıklama

Burada `x_0 ~ data` ve `x_1 ~ N(0, I)`. Bu düz çizgi boyunca zaman türevi sabittir:

```
dx_t / dt = x_1 - x_0
```

Bir sinirsel vektör alanı `v_θ(x_t, t)` tanımlayın ve bu türevle eşleşecek şekilde eğitin:

```
L = E_{x_0, x_1, t} || v_θ(x_t, t) - (x_1 - x_0) ||²
```

Bu, **koşullu flow matching** kaybıdır (Lipman 2023). Eğitim simülasyonsuzdur: ODE'yi asla açmazsınız. Sadece `(x_0, x_1, t)` örnekleme yapın ve regresyon yapın.

### Örnekleme

Çıkarımda, öğrenilen vektör alanını zamanda *geriye* doğru entegre edin:

```
x_{t-Δt} = x_t - Δt · v_θ(x_t, t)
```

`x_1 ~ N(0, I)`'den başlayın, `t=0`'a kadar Euler adımıyla inin.

### Rectified flow (Liu 2022)

Düz çizgi flow'u çalışır, ancak öğrenilen yollar aslında *düz değildir* — birçok `x_0` aynı `x_1`'e eşlenebileceği için kavislenir. Rectified flow'un reflow adımı:

1. Rastgele eşleştirmelerle flow modeli v_1 eğitin.
2. v_1'i `x_1`'den iniş yaptığı `x_0`'a kadar entegre ederek N çift `(x_1, x_0)` örnekleme yapın.
3. Bu eşleştirilmiş örnekler üzerinde v_2 eğitin. Çiftler artık "ODE-eşleştirilmiş" olduğu için, aralarındaki düz çizgi interpolant gerçekten daha düz olur.
4. Tekrarlayın.

Pratikte 2 reflow yinelemesi near-linear (doğrusala yakın) ulaşmanızı sağlar, 2-4 adım çıkarımı mümkün kılar. SDXL-Turbo, SD3-Turbo, LCM, flow matching'den distile edilmiş modellerdir.

### Neden 2024'te görseller için kazandı

Üç neden:

1. **Simülasyonsuz eğitim** — eğitim sırasında ODE açma yok, uygulaması kolay.
2. **Daha iyi kayıp geometrisi** — düz yollar tutarlı sinyal-gürültü oranına sahiptir, oysa DDPM ε-kayıp programının (schedule) kenarlarında kötü SNR'a sahiptir.
3. **Daha hızlı çıkarım** — SDXL-Turbo kalitesinde 4-8 adım; consistency distillation ile 1 adım.

## Flow matching vs DDPM — tam bağlantı

Gaussian-koşullu yol ile flow matching, *belirli bir gürültü programıyla* diffüzyondur. `x_t = α(t) x_0 + σ(t) x_1` programını seçin ve flow matching, `v = α'·x_0 - σ'·x_1` ile Stratonovich yeniden formüle edilmiş diffüzyonu recover eder. Gaussian yollar için ikisi cebirsel olarak eşdeğerdir.

Flow matching'in eklediği: hedefin *netliği* (düz bir hız), daha temiz bir kayıp ve Gauss olmayan interpolant'larla deneme lisansı.

## İnşa Et

`code/main.py`, iki-modlu Gaussian karma dağılımı (Gaussian mixture) üzerinde 1-D flow matching uygular. Vektör alanı `v_θ(x, t)`, düz çizgi hedefiyle eğitilmiş küçük bir MLP'dir. Çıkarımda 1, 2, 4 ve 20 Euler adımı entegre edin ve örnekleme kalitesini karşılaştırın.

### Adım 1: eğitim kaybı

```python
def train_step(x0, net, rng, lr):
    x1 = rng.gauss(0, 1)
    t = rng.random()
    x_t = t * x1 + (1 - t) * x0
    target = x1 - x0
    pred = net_forward(x_t, t)
    loss = (pred - target) ** 2
    # backprop + update
```

### Adım 2: çoklu adım çıkarımı

```python
def sample(net, num_steps):
    x = rng.gauss(0, 1)
    for i in range(num_steps):
        t = 1.0 - i / num_steps
        dt = 1.0 / num_steps
        x -= dt * net_forward(x, t)
    return x
```

### Adım 3: adım sayılarını karşılaştırın

4 adımlı örneleyicinin 20 adımlık kaliteye çoktan eşleşmesini bekleyin — gecikme için büyük bir mesele.

## Tuzaklar

- **Zaman parametrizasyonu.** Flow matching `t ∈ [0, 1]` kullanır, `t=0` veride, `t=1` gürültüde. DDPM `t ∈ [0, T]` kullanır, `t=0` veride, `t=T` gürültüde. Aynı yön, farklı ölçek. Makaleler bunu sürekli yanlış yazar.
- **Program seçimi.** Rectified flow'un düz çizgisi "the" flow matching programıdır, ancak daha iyi ölçek kapsama alanı için cosine veya logit-normal t-örneklemi (SD3 bunu yapar) kullanabilirsiniz.
- **Reflow maliyeti.** Reflow için eşleştirilmiş veri seti oluşturmak, örnek başına tam bir çıkarım geçişi. Yalnızca gerçekten 1-2 adım çıkarma gerektiğinde reflow yapın.
- **Classifier-free guidance hâlâ geçerli.** Sadece lineer kombinasyonda ε'yi v ile değiştirin: `v_cfg = (1+w) v_cond - w v_uncond`.

## Kullan

| Kullanım durumu | 2026 stack'i |
|----------------|-------------|
| Metinden-görsel, en iyi kalite | Flow matching: SD3, Flux.1-dev |
| Metinden-görsel, 1-4 adım | Distile flow matching: Flux.1-schnell, SD3-Turbo, SDXL-Turbo |
| Gerçek zamanlı çıkarım | Flow-matching tabanından consistency distillation (LCM, PCM) |
| Ses üretimi | Flow matching: Stable Audio 2.5, AudioCraft 2 |
| Video üretimi | Diffüzyonla harmanlanmış flow matching (Sora, Veo, Stable Video) |
| Bilim / fizik (parçacık yörüngeleri, moleküller) | Flow matching + eş varyantlı (equivariant) vektör alanı |

2025-2026'da bir makale "diffüzyondan daha hızlı" dediğinde, neredeyse her zaman flow matching + distillation'dır.

## Teslim Et

`outputs/skill-fm-tuner.md` dosyasını kaydedin. Skill bir diffüzyon tarzı model şablonu alır ve onu bir flow matching eğitim yapılandırmasına dönüştürür: program seçimi, zaman örneklemi dağılımı (uniform / logit-normal), optimize edici, reflow planı, hedef adım sayısı, eval protokolü.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın ve 1-adımlık ile 20-adımlık MSE'yi gerçek veri dağılımına göre karşılaştırın.
2. **Orta.** Uniform `t` örneklemeden logit-normale geçin (örneklemeyi orta-değerlerde yoğunlaştırır). Model kalitesi iyileşir mi?
3. **Zor.** Bir reflow yinelemesi uygulayın: ilk modeli entegre ederek eşleştirilmiş (x_0, x_1) üretin, çiftler üzerinde ikinci bir model eğitin ve 1-adımlık örnekleme kalitesini karşılaştırın.

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| Flow matching | "Düz çizgi diffüzyonu" | `v_θ(x, t)`'yi interpolant boyunca `x_1 - x_0` ile eşleşecek şekilde eğitmek. |
| Rectified flow | "Reflow" | Öğrenilen flow'ları düzleştiren yinelemeli prosedür. |
| Hız alanı | "v_θ" | Modelin çıktısı — `x_t`'nin hareket edeceği yön. |
| Düz çizgi interpolant | "Yol" | `x_t = (1-t)·x_0 + t·x_1`; basit hedef türevi. |
| Euler örneleyicisi | "1. mertebe ODE çözücü" | En basit entegratör; yollar düz olduğunda iyi çalışır. |
| Logit-normal t | "SD3 örnekleme" | Gradyanların en güçlü olduğu orta-değerlere `t` örneklemini yoğunlaştırır. |
| Consistency distillation | "1-adımlı örneleyici" | Herhangi bir `x_t`'yi doğrudan `x_0`'a eşleyen bir öğrenci eğitmek. |
| Hız ile CFG | "v-CFG" | `v_cfg = (1+w) v_cond - w v_uncond`; aynı numara, yeni değişken. |

## Üretim notu: Flux.1-schnell, flow matching'in en hızlısıdır

Flow matching'in üretim zaferi Flux.1-schnell — Flux-dev kalitesini koruyarak 1-4 çıkarım adımına distile edilmiş bir flow-matching DiT. Niels'in "8GB makinede Flux'u Çalıştırma" notebook'u referans dağıtım reçetesidir: T5 + CLIP kodlama, kantize MMDiT gürültü temizleme (schnell için 4 adımda, dev için 50 adımda), VAE decode. Maliyet hesabı:

| Varyant | Adımlar | 1024²'de L4 gecikmesi | Toplam FLOP (göreceli) |
|---------|---------|----------------------|------------------------|
| Flux.1-dev (ham) | 50 | ~15 sn | 1.0× |
| Flux.1-schnell | 4 | ~1.2 sn | 0.08× (12× daha hızlı) |
| SDXL-base | 30 | ~4 sn | 0.25× |
| SDXL-Lightning 2-step | 2 | ~0.3 sn | 0.03× |

Üretim kuralı: **flow-matching tabanı + distillation = 2026'da hızlı metinden-görsel için varsayılan.** Her büyük sağlayıcı bu kombinasyonu sunar: SD3-Turbo (SD3 + flow + distillation), Flux-schnell (Flux-dev + rectified-flow düzleştirme), CogView-4-Flash. Saf diffüzyon tabanları yalnızca eski checkpoint'ler için mevcuttur.

## Daha Fazla Kaynak

- [Liu, Gong, Liu (2022). Flow Straight and Fast: Learning to Generate and Transfer Data with Rectified Flow](https://arxiv.org/abs/2209.03003) — rectified flow.
- [Lipman ve ark. (2023). Flow Matching for Generative Modeling](https://arxiv.org/abs/2210.02747) — flow matching.
- [Esser ve ark. (2024). Scaling Rectified Flow Transformers for High-Resolution Image Synthesis](https://arxiv.org/abs/2403.03206) — SD3, ölçekli rectified flow.
- [Albergo, Vanden-Eijnden (2023). Stochastic Interpolants](https://arxiv.org/abs/2303.08797) — FM + diffüzyonu kapsayan genel çerçeve.
- [Song ve ark. (2023). Consistency Models](https://arxiv.org/abs/2303.01469) — diffüzyon / flow'un 1-adımlı distilasyonu.
- [Sauer ve ark. (2023). Adversarial Diffusion Distillation (SDXL-Turbo)](https://arxiv.org/abs/2311.17042) — turbo varyantı.
- [Black Forest Labs (2024). Flux.1 modelleri](https://blackforestlabs.ai/announcing-black-forest-labs/) — üretimde flow matching.
