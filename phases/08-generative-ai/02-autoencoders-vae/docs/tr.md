# Autoencoder'lar (Öz-Çözücüler) ve Variational Autoencoders (VAE)

> Düz bir autoencoder sıkıştırır ve yeniden oluşturur. Ezberler. Üretmez. Bir hile ekleyin — kodun Gauss görünmesini zorlayın — ve bir örnekleyici elde edersiniz. Tek bu hile — `z = μ + σ·ε` reparameterization (yeniden parametrelendirme) hilesi — 2026'da kullandığınız her latent-diffusion ve flow matching görüntü modelinin girişinde bir VAE bulunduğu anlamına gelir.

**Tür:** Oluşturma
**Diller:** Python
**Önkoşullar:** Faz 3 · 02 (Backprop), Faz 3 · 07 (CNN'ler), Faz 8 · 01 (Sınıflandırma)
**Süre:** ~75 dakika

## Problem

784 piksel bir MNIST rakamını 16 sayılık bir koda sıkıştırın ve yeniden oluşturun. Düz bir autoencoder yeniden oluşturma MSE'sinde mükemmeldir ama kod alanı düzensiz bir karmaşıklıktır. Kod alanından rastgele bir nokta seçin, onu çözün ve gürültü elde edersiniz. Örnekleyicisi yoktur. Sadece giydirilmiş bir sıkıştırma modelidir.

Aslında istediğiniz şudur: (a) kod alanı temiz, pürüzsüz bir dağılımdır — örneğin izotropik Gauss `N(0, I)` — (b) herhangi bir örneği çözmek makul bir rakam üretir ve (c) encoder ve decoder hâlâ iyi sıkıştırır. Üç hedef, bir mimari, bir kayıp.

Kingma'nın 2013 VAE'si bunu encoder'ı bir *dağılım* `q(z|x) = N(μ(x), σ(x)²)` verecek şekilde eğiterek, bu dağıtımı prior `N(0, I)`'ye KL cezasıyla çekerek ve ardından `z`'yi `q(z|x)`'den örnekleyerek çözer. Inference zamanında encoder'ı bırakın, `z ~ N(0, I)` örnekleyin, çözün. KL cezası kod alanını yapılandıran şeydir.

2026'da VAE'ler nadiren bağımsız olarak sunulur — ham görüntü kalitesinde diffusion tarafından geçilmişlerdir — ama her latent-diffusion modelinin (SD 1/2/XL/3, Flux, AudioCraft) tercih edilen encoder'ıdır. VAE'yi öğrenirseniz, kullandığınız her görüntü hattının görünmez ilk katmanını öğrenmiş olursunuz.

## Kavram

![Autoencoder vs VAE: reparameterization hilesi](../assets/vae.svg)

**Autoencoder.** `z = encoder(x)`, `x̂ = decoder(z)`, kayıp = `||x - x̂||²`. Kod alanı yapılandırılmamış.

**VAE encoder.** İki vektör çıktı verir: `μ(x)` ve `log σ²(x)`. Bunlar `q(z|x) = N(μ, diag(σ²))` dağılımını tanımlar.

**Reparameterization hilesi.** `q(z|x)`'den örneklemek türev alınabilir değildir. Örneği `z = μ + σ·ε` olarak yeniden yazın, burada `ε ~ N(0, I)`. Artık `z`, `(μ, σ)`'nun deterministik bir fonksiyonu artı parametrik olmayan bir gürültüdür — gradyanlar `μ` ve `σ` üzerinden akar.

**Kayıp.** Evidence Lower Bound (ELBO), iki terim:

```
loss = reconstruction + β · KL[q(z|x) || N(0, I)]
     = ||x - x̂||²  + β · Σ_i ( σ_i² + μ_i² - log σ_i² - 1 ) / 2
```

#### Açıklama
Yeniden oluşturma terimi `x̂`'yi `x`'e doğru iter. KL terimi `q(z|x)`'i prior'a doğru iter. Arasında bir denge vardır. Küçük β (<1) = daha keskin örnekler, kod alanı daha az Gauss. Büyük β (>1) = daha temiz kod alanı, daha bulanık örnekler. β-VAE (Higgins 2017) bu ayarı ünlü yaptı ve ayrıştırma (disentanglement) araştırmalarını başlattı.

**Örnek alma.** Inference'ta: `z ~ N(0, I)` örnekle, decoder'dan geçir. Tek bir forward pass — diffusion'daki gibi iteratif örnek alma yoktur.

## Kodu Oluştur

`code/main.py`, numpy veya torch olmadan küçük bir VAE uygular. Girdi, 8 boyutlu sentetik veriden oluşur — 8 boyutlu 2 bileşenli bir Gaussian karışımından çizilmiş. Encoder ve decoder tek gizli katmanlı MLP'lerdir. Tanh aktivasyonu, forward pass, kayıp ve el yazısı backward pass uygularız. Üretim amaçlı değil, pedagojik amaçlıdır.

### Adım 1: encoder forward

```python
def encode(x, enc):
    h = tanh(add(matmul(enc["W1"], x), enc["b1"]))
    mu = add(matmul(enc["W_mu"], h), enc["b_mu"])
    log_sigma2 = add(matmul(enc["W_sig"], h), enc["b_sig"])
    return mu, log_sigma2
```

#### Açıklama
`log σ²` kullanıyoruz `σ` yerine çünkü ağ çıktısı kısıtsız olmalı (σ'nun softplus'ı bir tuzaktır — gradyanlar σ ≈ 0'da ölür).

### Adım 2: reparameterize ve decode

```python
def reparameterize(mu, log_sigma2, rng):
    eps = [rng.gauss(0, 1) for _ in mu]
    sigma = [math.exp(0.5 * lv) for lv in log_sigma2]
    return [m + s * e for m, s, e in zip(mu, sigma, eps)]

def decode(z, dec):
    h = tanh(add(matmul(dec["W1"], z), dec["b1"]))
    return add(matmul(dec["W_out"], h), dec["b_out"])
```

#### Açıklama
Reparameterization hilesi, örnekleme işlemini türev alınabilir hale getirir.

### Adım 3: ELBO

```python
def elbo(x, x_hat, mu, log_sigma2, beta=1.0):
    recon = sum((a - b) ** 2 for a, b in zip(x, x_hat))
    kl = 0.5 * sum(math.exp(lv) + m * m - lv - 1 for m, lv in zip(mu, log_sigma2))
    return recon + beta * kl, recon, kl
```

#### Açıklama
Her iki dağılım da Gauss olduğu için kesin kapalı formda KL elde ederiz. Sayısal olarak integral almayın. 2026'da hala monte-carlo KL tahminleriyle kod yayınlayanlar var — bu gereksiz yere 3x daha yavaştır.

### Adım 4: üret

```python
def sample(dec, z_dim, rng):
    z = [rng.gauss(0, 1) for _ in range(z_dim)]
    return decode(z, dec)
```

#### Açıklama
İşte generatif model. Beş satır.

## Tuzaklar

- **Posterior collapse (Posterior çökmesi).** KL terimi `q(z|x) → N(0, I)` ifadesini o kadar agresif bir şekilde iter ki `z`, `x` hakkında bilgi taşımaz. Çözüm: β-annealing (β=0'dan başla, 1'e rampa yap), free bits veya boyutlar arası KL'yi atla.
- **Bulanık örnekler.** Gauss decoder likelihood'ı MSE yeniden oluşturmasını ima eder, bu da L2 (ortalama) için Bayes-optimaldir — birçok olası rakamın ortalaması bulanık bir rakamdır. Çözüm: discrete decoder (VQ-VAE, NVAE) veya VAE'yi sadece encoder olarak kullanıp latent'lerin üzerine diffusion istifleyin (Stable Diffusion'ın yaptığı budur).
- **β çok büyük, çok erken.** Posterior collapse'a bakın. β≈0.01'den başlayın ve rampa yapın.
- **Latent boyut çok küçük.** 16-D MNIST için işe yarar, ImageNet 256² için 256-D, ImageNet 1024² için 2048-D. Stable Diffusion'ın VAE'si 512×512×3 → 64×64×4 sıkıştırır (alan açısından 32x alt örnekleme faktörü, kanallarda 32x).

## Kullan

2026 VAE yığını:

| Durum | Seçin |
|-----------|------|
| Diffusion için görüntü-latent encoder | Stable Diffusion VAE (`sd-vae-ft-ema`) veya Flux VAE |
| Ses-latent encoder | Encodec (Meta), SoundStream veya DAC (Descript) |
| Video latent'leri | Sora'nın zamansal-mekansal patch'leri, Latte VAE, WAN VAE |
| Ayrılmış temsil öğrenimi | β-VAE, FactorVAE, TCVAE |
| Discrete latent'ler (transformer modellemesi için) | VQ-VAE, RVQ (ResidualVQ) |
| Üretim için sürekli latent'ler | Düz VAE, ardından o latent uzayında bir flow/diffusion modelini koşullandırın |

Latent-diffusion modeli, encoder ve decoder arasında yaşayan bir diffusion modeli olan bir VAE'dir. VAE kaba sıkıştırmayı yapar, diffusion modeli ağır işi yapar. Aynı patern video için (VAE + video-diffusion DiT) ve ses için (Encodec + MusicGen transformer) geçerlidir.

## Sun

`outputs/skill-vae-trainer.md` olarak kaydedin.

Beceri şunları alır: veri seti profili + latent-boyut hedefi + aşağı akım kullanımı (yeniden oluşturma, örnekleme veya latent-diffusion girdisi) ve şunları çıktı olarak verir: mimari seçimi (düz/β/VQ/RVQ), β programı, latent boyut, decoder likelihood'ı (Gauss vs kategorik) ve değerlendirme planı (yeniden oluşturma MSE, boyut başına KL, `q(z|x)` ile `N(0, I)` arası Fréchet mesafesi).

## Alıştırmalar

1. **Kolay.** `code/main.py` dosyasındaki `β` değerini `0.01`, `0.1`, `1.0`, `5.0` olarak değiştirin. Son yeniden oluşturma MSE'sini ve KL değerini kaydedin. Sentetik veriniz için hangi β Pareto-optimaldir?
2. **Orta.** Gauss decoder likelihood'ını Bernoulli likelihood'ı ile değiştirin (cross-entropy kaybı). Aynı sentetik verinin binarize edilmiş versiyonu üzerinde örnek kalitesini karşılaştırın.
3. **Zor.** `code/main.py` dosyasını mini bir VQ-VAE'ye genişletin: sürekli `z`'yi K=32 girdili bir codebook'ta en yakın komşu aramasıyla değiştirin. Yeniden oluşturma MSE'sini karşılaştırın ve kaç codebook girdisinin kullanıldığını bildirin (codebook collapse gerçekten olur).

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|------|-----------------|-----------------------|
| Autoencoder (Öz-çözücü) | Encode-decoder ağı | `x → z → x̂`, MSE öğrenir. Generatif değildir. |
| VAE | Örnekleyicili AE | Encoder bir dağılım çıktı verir, KL cezası kod alanını şekillendirir. |
| ELBO | Evidence lower bound | `log p(x) ≥ recon - KL[q(z\|x) \|\| p(z)]`; `q = p(z\|x)` olduğunda sıkıdır. |
| Reparameterization (Yeniden parametrelendirme) | `z = μ + σ·ε` | Stokastik düğümü deterministik + saf gürültü olarak yeniden yazar. Örnekleme üzerinden backprop'u sağlar. |
| Prior (Önceki) | `p(z)` | Latent için hedef dağılım, genellikle `N(0, I)`. |
| Posterior collapse (Posterior çökmesi) | "KL terimi kazanır" | Encoder `x`'i görmezden gelir, prior'u çıktı verir; decoder hayal gücüne başvurmak zorunda kalır. |
| β-VAE | Ayarlanabilir KL ağırlığı | `loss = recon + β·KL`. Daha yüksek β = daha ayrıştırılmış ama daha bulanık. |
| VQ-VAE | Discrete latent | Sürekli `z`'yi en yakın codebook vektörüyle değiştirin; transformer modellemesini sağlar. |

## Üretim notu: VAE bir diffusion sunucusunda en sıcak yoldur

Bir Stable Diffusion / Flux / SD3 hattında VAE istek başına iki kez çağrılır — bir kez kodlamak için (img2img / inpainting yapıyorsanız) ve bir kez çözmek için. 1024²'nde decoder pass'ı genellikle tüm hattın en büyük aktivasyon bellek zirvesidir çünkü `128×128×16` latent'leri `1024×1024×3`'e geri örnekleme yapar. İki pratik sonuç:

- **Decode işlemini dilimleyin veya döşeyin.** `diffusers` `pipe.vae.enable_slicing()` ve `pipe.vae.enable_tiling()` seçeneklerini sunar. Döşeme, `O(döşeme²)` bellek karşılığında küçük bir dikiş hatası verir `O(H·W)` yerine. Tüketici GPU'larında 1024²+ için gereklidir.
- **bf16 decoder, son yeniden boyutlandırma için fp32 numerikleri.** SD 1.x VAE'si fp32 olarak yayınlandı ve 1024²+'de fp16'ya dönüştürüldüğünde *sessizce NaN üretir*. SDXL `madebyollin/sdxl-vae-fp16-fix` ile yayınlandı — her zaman fp16-fix varyantını tercih edin veya bf16 kullanın.

## Daha Fazla Kaynak

- [Kingma & Welling (2013). Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114) — VAE makalesi.
- [Higgins et al. (2017). β-VAE: Learning Basic Visual Concepts with a Constrained Variational Framework](https://openreview.net/forum?id=Sy2fzU9gl) — ayrıştırılmış β-VAE.
- [van den Oord et al. (2017). Neural Discrete Representation Learning](https://arxiv.org/abs/1711.00937) — VQ-VAE.
- [Vahdat & Kautz (2021). NVAE: A Deep Hierarchical Variational Autoencoder](https://arxiv.org/abs/2007.03898) — en iyi durumdaki görüntü VAE'si.
- [Rombach et al. (2022). High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752) — Stable Diffusion; VAE encoder olarak.
- [Défossez et al. (2022). High Fidelity Neural Audio Compression](https://arxiv.org/abs/2210.13438) — Encodec, ses VAE standardı.
