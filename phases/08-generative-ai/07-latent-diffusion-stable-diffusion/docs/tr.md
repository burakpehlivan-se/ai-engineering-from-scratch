# Latent Diffusion & Stable Diffusion

> 512×512 görseller üzerinde piksel-uzayı diffüzyonu (pixel-space diffusion) bir savaş suçudur. Rombach ve ark. (2022), bir görsel üretmek için 786 bin boyutun tamamına gerek olmadığını fark etti — semantic yapıyı yakalayacak kadar yeterli ve geri kalan için ayrı bir decoder yeterli. Diffüzyonu bir VAE'nin latent uzayında çalıştırın. Tek bir fikir, Stable Diffusion'ı doğurdu.

**Tür:** İnşa Et
**Diller:** Python
**Ön koşullar:** Faz 8 · 02 (VAE), Faz 8 · 06 (DDPM), Faz 7 · 09 (ViT)
**Süre:** ~75 dakika

## Problem

512² piksel uzayında diffüzyon, U-Net'in `[B, 3, 512, 512]` boyutunda tensörler üzerinde çalışması demektir. Her örnekleme (sampling) adımı, 500 milyon parametreli bir U-Net için yaklaşık 100 GFLOPS harcar. Elli adım, görsel başına 5 TFLOPS demektir. Milyarlarca görsel üzerinde eğitildiğinde fatura absürt bir hal alır.

Bu FLOP'ların çoğu, algısal olarak önemli olmayan detayları — kayıplı bir VAE'nin sıkıştırabileceği yüksek frekanslı dokuyu — ağdan geçirir. Rombach'ın fikri: bir kez VAE eğitin (*birinci aşama*), dondurun ve diffüzyonu tamamen 4 kanallı 64×64 latent uzayında çalıştırın (*ikinci aşama*). Aynı U-Net. 1/16 piksel. Benzer kalite için yaklaşık 64 kat daha az FLOP.

Bu, Stable Diffusion reçetesidir. SD 1.x / 2.x, `64×64×4` latent'ler üzerinde 860M U-Net kullandı; SDXL `128×128×4` üzerinde 2.6B U-Net kullandı; SD3 ise U-Net'i flow matching ile çalışan bir Diffusion Transformer (DiT) ile değiştirdi. Flux.1-dev (Black Forest Labs, 2024) 12B parametreli bir DiT-MMDiT sunuyor. Tümü aynı iki aşamalı altyapı üzerinde çalışıyor.

## Kavram

![Latent diffüzyon: VAE sıkıştırma + latent uzayda diffüzyon](../assets/latent-diffusion.svg)

**İki aşamalı, ayrı ayrı eğitilmiş.**

1. **Aşama 1 — VAE.** Encoder `E(x) → z`, decoder `D(z) → x`. Hedef sıkıştırma: her eksende 8× downsampling + toplam latent boyutunu piksel sayısının yaklaşık 1/16'sı olacak şekilde kanal ayarlaması. Kayıp = yeniden oluşturma (L1 + LPIPS algısal) + KL (küçük ağırlık, böylece `z` çok fazla Gaussiana zorlanmaz, çünkü `z`'den tam örnekleme yapmaya gerek yok). Genellikle decoded görsellerin keskin olması için adversarial kayıpla birlikte eğitilir.

2. **Aşama 2 — `z` üzerinde diffüzyon.** `z = E(x_real)` veri olarak ele alınır. Bir U-Net (veya DiT) `z_t`'yi gürültüden arındırmak için eğitilir. Çıkarım (inference) sırasında: diffüzyon ile `z_0` örnekleme yapılır, ardından `x = D(z_0)` ile decode edilir.

**Metin koşullandırması (text conditioning).** İki ek bileşen. Donmuş bir metin encoder'ı (SD 1.x için CLIP-L, SD 2/XL için CLIP-L+OpenCLIP-G, SD3 ve Flux için T5-XXL). Bir cross-attention enjeksiyonu: her U-Net bloğu `[Q = görüntü özellikleri, K = V = metin token'ları]` alır ve bunları harmanlar. Token'lar, metnin görseli etkilemesinin tek yoludur.

**Kayıp fonksiyonu Ders 06 ile aynıdır.** Gürültü üzerinde aynı DDPM / flow matching MSE. Sadece veri alanını değiştirirsiniz.

## Mimari varyantlar

| Model | Yıl | Omurga | Latent boyutu | Metin encoder'ı | Parametreler |
|-------|-----|--------|---------------|-----------------|--------------|
| SD 1.5 | 2022 | U-Net | 64×64×4 | CLIP-L (77 token) | 860M |
| SD 2.1 | 2022 | U-Net | 64×64×4 | OpenCLIP-H | 865M |
| SDXL | 2023 | U-Net + refiner | 128×128×4 | CLIP-L + OpenCLIP-G | 2.6B + 6.6B |
| SDXL-Turbo | 2023 | Distilled | 128×128×4 | aynı | 1-4 adım örnekleme |
| SD3 | 2024 | MMDiT (multimodal DiT) | 128×128×16 | T5-XXL + CLIP-L + CLIP-G | 2B / 8B |
| Flux.1-dev | 2024 | MMDiT | 128×128×16 | T5-XXL + CLIP-L | 12B |
| Flux.1-schnell | 2024 | MMDiT distilled | 128×128×16 | T5-XXL + CLIP-L | 12B, 1-4 adım |

Eğilim: U-Net'i DiT ile değiştirme (latent patch'ler üzerinde transformer), metin encoder'ını ölçeklendirme (T5, prompt uyumu için CLIP'i yener), latent kanallarını artırma (4 → 16 daha fazla detay alanı sağlar).

## İnşa Et

`code/main.py`, bir oyuncak 1-D "VAE" (eğitim amaçlı; gerçek bir VAE bir conv net olurdu) ile Lesson 06'daki DDPM'i birleştirir ve classifier-free guidance ile sınıf koşullandırması ekler. Aynı diffüzyon kaybının ham 1-D değerler üzerinde mi yoksa kodlanmış değerler üzerinde mi çalıştığını — temel içgörümü — gösterir.

### Adım 1: encoder/decoder

```python
def encode(x):    return x * 0.5          # toy "compression" to smaller scale
def decode(z):    return z * 2.0
```

#### Açıklama

Gerçek bir VAE'nin eğitilmiş ağırlıkları vardır. Pedagojik olarak, bu lineer harita diffüzyonun `z` üzerinde orijinal veri alanına bakmadan çalıştığını göstermek için yeterlidir.

### Adım 2: `z`-uzayında diffüzyon

Ders 06 ile aynı DDPM. Ağın gördüğü veri `z = E(x)`. `z_0` örneklendikten sonra `D(z_0)` ile decode edilir.

### Adım 3: classifier-free guidance

Eğitim sırasında, sınıf etiketini %10 oranında düşürün (null token ile değiştirin). Çıkarım sırasında hem `ε_cond` hem de `ε_uncond` hesaplayın, ardından:

```python
eps_cfg = (1 + w) * eps_cond - w * eps_uncond
```

#### Açıklama

`w = 0` = yönlendirme yok (tam çeşitlilik), `w = 3` = varsayılan, `w = 7+` = doymuş / aşırı keskin.

### Adım 4: metin koşullandırması (kavram, kod değil)

Sınıf etiketini donmuş bir metin encoder çıktısıyla değiştirin. Metin embedding'ini U-Net'e cross-attention aracılığıyla besleyin:

```python
h = h + CrossAttention(Q=h, K=text_embed, V=text_embed)
```

#### Açıklama

Bu, sınıf-koşullu bir diffüzyon modeli ile Stable Diffusion arasındaki tek substantive farktır.

## Tuzaklar

- **VAE-ölçek uyumsuzluğu.** SD 1.x VAE'leri kodlamadan sonra uygulanan bir ölçeklendirme sabitine (`scaling_factor ≈ 0.18215`) sahiptir. Bunu unutmak, U-Net'in yanlış varyansa sahip latent'ler üzerinde eğitilmesine neden olur. Her checkpoint bir tane içerir.
- **Metin encoder'ı sessizce yanlış.** SD3, >=128 token ile T5-XXL gerektirir ve sadece CLIP'e geri dönüş kayıplıdır. Her zaman `use_t5=True` olup olmadığını kontrol edin, aksi halde prompt sadakati düşer.
- **Latent uzay karıştırma.** SDXL, SD3, Flux farklı VAE'ler kullanır. SDXL latent'leri üzerinde eğitilmiş bir LoRA, SD3 üzerinde çalışmaz. Hugging Face diffusers 0.30+, uyumsuz checkpoint'leri yüklemeyi reddeder.
- **CFG çok yüksek.** `w > 10` doymuş, yağlı görseller üretir ve çeşitlilik pahasına prompt'a aşırı uyum sağlar. İdeal aralık `w = 3-7`'dir.
- **Negatif prompt sızıntısı.** Boş negatif prompt null token olur; dolu negatif prompt ise `ε_uncond` olur. Bunlar aynı değildir; bazı pipeline'lar sessizce null'a varsayar.

## Kullan

2026'daki üretim stack'leri:

| Hedef | Önerilen omurga |
|-------|-----------------|
| Dar alan, eşleştirilmiş veri, sıfırdan model eğitimi | SDXL fine-tune (LoRA / tam) — en hızlı teslimat |
| Açık alan metinden-görsel, açık ağırlıklar | Flux.1-dev (12B, Apache / ticari olmayan) veya SD3.5-Large |
| En hızlı çıkarım, açık ağırlıklar | Flux.1-schnell (1-4 adım, Apache) veya SDXL-Lightning |
| En iyi prompt uyumu, barındırma | GPT-Image / DALL-E 3 (hala), Midjourney v7, Imagen 4 |
| Düzenleme iş akışları | Flux.1-Kontext (Aralık 2024) — doğal olarak görsel + metin kabul eder |
| Araştırma, temel hat | SD 1.5 — eski ama iyi çalışılmış |

## Teslim Et

`outputs/skill-sd-prompter.md` dosyasını kaydedin. Skill bir metin prompt'u + hedef stil alır ve çıktı olarak şunları verir: model + checkpoint, CFG ölçeği, örnekleme yöntemi (sampler), negatif prompt, çözünürlük, isteğe bağlı ControlNet/IP-Adapter kombinasyonu ve adım başına QA kontrol listesi.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi `w ∈ {0, 1, 3, 7, 15}` yönlendirmesiyle çalıştırın. Sınıf başına ortalama örnekleme kaydedin. Hangi `w`'de sınıf ortalamaları gerçek veri ortalamalarından sapar?
2. **Orta.** Oyuncak lineer encoder'ı, yeniden oluşturma kaybına sahip bir tanh-MLP encoder/decoder çiftiyle değiştirin. Yeni latent'ler üzerinde diffüzyonu yeniden eğitin. Örnekleme kalitesi değişiyor mu?
3. **Zor.** Diffusers ile gerçek bir Stable Diffusion çıkarımı kurun: `sdxl-base` yükleyin, CFG=7 ile 30 Euler adımı çalıştırın ve zamanlayın. Şimdi `sdxl-turbo`'ya 4 adım ve CFG=0 ile geçin. Aynı konu, farklı kalite — ne değişti ve neden açıklayın.

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| Birinci aşama | "VAE" | Eğitilmiş encoder/decoder çifti; 512²'yi 64²'ye sıkıştırır. |
| İkinci aşama | "U-Net" | Latent uzayı üzerindeki diffüzyon modeli. |
| CFG | "Guidance ölçeği" | `(1+w)·ε_cond - w·ε_uncond`; koşullandırma gücünü ayarlar. |
| Null token | "Boş prompt embed" | `ε_uncond` için kullanılan koşulsuz embed. |
| Cross-attention | "Metin nasıl girer" | Her U-Net bloğu metin token'larını K ve V olarak dikkate alır. |
| DiT | "Diffusion Transformer" | U-Net'i latent patch'ler üzerinde transformer ile değiştirir; daha iyi ölçeklenir. |
| MMDiT | "Multi-modal DiT" | SD3'ün mimarisi: birlikte dikkate sahip metin ve görüntü akışları. |
| VAE ölçeklendirme faktörü | "Sihirli sayı" | Latent'leri ~5.4'e böler, böylece diffüzyon birim varyanslı uzayda çalışır. |

## Üretim notu: Flux-12B'yi 8GB tüketici GPU'sunda çalıştırma

referans Flux entegrasyonu, "Tüketici GPU'm var, bunu üretebilir miyim?" sorusunun kanonik reçetesidir. Numara, üretim çıkarım literatüründen alınan aynı üç ayarlı reçetenin diffüzyon DiT'ine uygulanmasıdır:

1. **Aşamalı yükleme.** Flux'un VRAM'de bir arada bulunmasına gerek olmayan üç ağı vardır: T5-XXL metin encoder'ı (fp32'de ~10 GB), CLIP-L (küçük), 12B MMDiT ve VAE. Önce promptu kodlayın, encoder'ları *silin*, DiT'i yükleyin, gürültüyü arındırın, DiT'i *silin*, VAE'yi yükleyin, decode edin. Tüketici 8GB GPU'ları aynı anda yalnızca bir aşama sığdırabilir.
2. **bitsandbytes ile 4-bit kantizasyon (quantization).** Hem T5 encoder'ı hem de DiT için `BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)`. Belleği 8 kat azaltır, metinden-görselde kalite düşüşü Aritra'nın benchmark'larında hissedilemez (notebook'ta bağlantı verilmiştir).
3. **CPU deşarjı (offload).** `pipe.enable_model_cpu_offload()` her ileri geçiş ilerledikçe modülleri CPU ve GPU arasında otomatik olarak değiştirir. 10-20% gecikme ekler ama pipeline'ın çalışmasını sağlar.

Bellek hesabı: `10 GB T5 / 8 = 1.25 GB` kantize, `12 B parametre × 0.5 byte = ~6GB` kantize DiT, artı aktivasyonlar. stas00'ın terminolojisiyle bu, TP=1 çıkarımının en uç noktasıdır — model paralellliği yok, maksimum kantizasyon. Üretim ortamında H100'lerde TP=2 veya TP=2 çalıştırırdınız; tek bir geliştirme dizüstü bilgisayarı için bu reçetedir.

## Daha Fazla Kaynak

- [Rombach ve ark. (2022). High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752) — Stable Diffusion.
- [Podell ve ark. (2023). SDXL: Improving Latent Diffusion Models for High-Resolution Image Synthesis](https://arxiv.org/abs/2307.01952) — SDXL.
- [Peebles & Xie (2023). Scalable Diffusion Models with Transformers (DiT)](https://arxiv.org/abs/2212.09748) — DiT.
- [Esser ve ark. (2024). Scaling Rectified Flow Transformers for High-Resolution Image Synthesis](https://arxiv.org/abs/2403.03206) — SD3, MMDiT.
- [Ho & Salimans (2022). Classifier-Free Diffusion Guidance](https://arxiv.org/abs/2207.12598) — CFG.
- [Labs (2024). Flux.1 — Black Forest Labs announcement](https://blackforestlabs.ai/announcing-black-forest-labs/) — Flux.1 ailesi.
- [Hugging Face Diffusers docs](https://huggingface.co/docs/diffusers/index) — yukarıdaki her checkpoint için referans uygulama.
