# Video Üretimi

> Bir görsel 2 boyutlu bir tensördür. Bir video 3 boyutlusudur. Teori aynıdır; hesaplama 10-100 kat daha zordur. OpenAI'ın Sora'sı (Şubat 2024) bunun mümkün olduğunu kanıtladı. 2026'ya kadar Veo 2, Kling 1.5, Runway Gen-3, Pika 2.0 ve WAN 2.2, metinden 1080p'de üretim videosu sunuyor — ve açık ağırlıklar stack'i (CogVideoX, HunyuanVideo, Mochi-1, WAN 2.2) 12 ay geride.

**Tür:** İnşa Et
**Diller:** Python
**Ön koşullar:** Faz 8 · 07 (Latent Diffusion), Faz 7 · 09 (ViT), Faz 8 · 06 (DDPM)
**Süre:** ~45 dakika

## Problem

24fps'de 10 saniyelik 1080p video, 1920×1080×3 pikselinden oluşan 240 karedir. Bu, klibin ham veri olarak yaklaşık 1.5 GB'ıdır. Piksel-uzayı diffüzyonu uygulanamaz. Şunlara ihtiyacınız var:

1. **Uzamsal-zamansal sıkıştırma (spatiotemporal compression).** Kareleri değil, videoları uzamsal-zamansal yamalara (patches) dönüştüren bir VAE.
2. **Zamansal tutarlılık (temporal coherence).** Karelerin saniyeler boyunca içeriği, aydınlatmayı ve nesne kimliğini paylaşması gerekir. Ağ hareketi modellemelidir.
3. **Hesaplama bütçesi.** Video eğitimi, aynı model boyutu için görüntüden 10-100 kat daha pahalıdır.
4. **Koşullandırma (conditioning).** Metin, görsel (ilk kare), ses veya başka bir video. Üretim modellerinin çoğu dördünü de kabul eder.

Bu sorunu çözen mimari, devasa (prompt, caption, video) veri setleri üzerinde eğitilen, uzamsal-zamansal yamalara uygulanan **Diffusion Transformer (DiT)**'tır. Ders 06 ile aynı diffüzyon kaybı.

## Kavram

![Video diffüzyonu: yamalama, DiT, decode](../assets/video-generation.svg)

### Yamalama (Patchify)

Videoyu 3D VAE ile kodlayın (öğrenilen uzamsal-zamansal sıkıştırma). Latent `[T_latent, H_latent, W_latent, C_latent]` şeklindedir. `[t_p, h_p, w_p]` boyutunda yamalara bölün. Sora tarzı modeller için `t_p = 1` (kare başına yamalar) veya `t_p = 2` (her iki karede bir). 10 saniyelik 1080p video yaklaşık 20.000-100.000 yamaya sıkıştırılır.

### Uzamsal-zamansal DiT

Bir transformer düzleştirilmiş yama dizisini işler. Her yamanın 3 boyutlu konumsal embedding'i (zaman + y + x) vardır. Attention genellikle çarpanlı (factorized) kullanılır:

- **Uzamsal attention** her karenin yamaları içinde.
- **Zamansal attention** aynı uzamsal konumda kareler boyunca.
- **Tam 3D attention** 16-100 kat daha pahalıdır; yalnızca düşük çözünürlükte veya araştırmada kullanılır.

### Metin koşullandırması

Büyük bir metin encoder'ı ile cross-attention (Sora için T5-XXL, CogVideoX-5B T5-XXL kullanır). Uzun promptlar önemlidir — Sora'nın eğitim seti, klibin başına ortalama 200 token olan GPT tarafından üretilen yoğun yeniden açıklamalar (re-captions) içeriyordu.

### Eğitim

Uzamsal-zamansal latent'ler üzerinde standart diffüzyon kaybı (ε veya v tahmini). Veri: web videoları + ~100M özenle seçilmiş klip + sentetik metin açıklamaları. Hesaplama: küçük bir araştırma çalışması için bile 10.000+ GPU saati; ölçekli Sora için 100.000+.

## 2026 üretim manzarası

| Model | Tarih | Maks. süre | Maks. çözünürlük | Açık ağırlıklar? | Dikkat çekici |
|-------|-------|-----------|-----------------|------------------|--------------|
| Sora (OpenAI) | 2024-02 | 60s | 1080p | Hayır | Ölçekli dünya simülatörü özelliklerini gösteren ilk model |
| Sora Turbo | 2024-12 | 20s | 1080p | Hayır | 5 kat daha hızlı çıkarıma sahip üretim Sora'sı |
| Veo 2 (Google) | 2024-12 | 8s | 4K | Hayır | 2025'te en yüksek kalite + fizik |
| Veo 3 | 2025 Q3 | 15s | 4K | Hayır | Doğal ses ve daha güçlü kamera kontrolü |
| Kling 1.5 / 2.1 (Kuaishou) | 2024-2025 | 10s | 1080p | Hayır | 2025 Q1'de en iyi insan hareketi |
| Runway Gen-3 Alpha | 2024-06 | 10s | 768p | Hayır | Üzerinde profesyonel video araçları |
| Pika 2.0 | 2024-10 | 5s | 1080p | Hayır | En güçlü karakter tutarlılığı |
| CogVideoX (THUDM) | 2024 | 10s | 720p | Evet (2B, 5B) | İlk açık 5B ölçekli video |
| HunyuanVideo (Tencent) | 2024-12 | 5s | 720p | Evet (13B) | 2024 sonunda açık SOTA |
| Mochi-1 (Genmo) | 2024-10 | 5.4s | 480p | Evet (10B) | En izinli lisanslı |
| WAN 2.2 (Alibaba) | 2025-07 | 5s | 720p | Evet | 2025 ortasında en güçlü açık model |

Açık ağırlıklar, görüntü alanındaki boşluğu görüntü alanından daha hızlı kapatıyor: HunyuanVideo + WAN 2.2 LoRA'ları 2026 ortasına kadar çoğu açık kaynak iş akımını zaten destekliyor.

## İnşa Et

`code/main.py`, temel uzamsal-zamansal DiT fikrini simüle eder: küçük bir sentetik videoyu yamalar, yama başına konumsal embedding ekler ve transformer tarzı attention ile tüm diziyi temizler. numpy yok; saf Python. Komşu kare yamaları ortak bir gürültü temizleyici ve konumsal embedding'ler paylaştığında zamansal tutarlılığın 1-D'de bile nasıl ortaya çıktığını gösteriyoruz.

### Adım 1: sentetik 1-D "videoyu" yamalama

```python
def make_video(T_frames=8, rng=None):
    # a "video" is a sequence of 1-D values following a smooth trajectory
    base = rng.gauss(0, 1)
    return [base + 0.3 * t + rng.gauss(0, 0.1) for t in range(T_frames)]
```

#### Açıklama

"Video", düzgün bir yörünge izleyen 1-D değerler dizisidir. Bu, zamansal yapıyı modellemek için yeterlidir.

### Adım 2: kare başına konumsal embedding

```python
def pos_embed(t, dim):
    return sinusoidal(t, dim)
```

### Adım 3: gürültü temizleyici tüm diziyi görür

Her kareyi bağımsız olarak temizlemek yerine, küçük ağımız tüm kare değerlerini + konumsal embedding'lerini birleştirir ve tüm kareler için gürültüyü birlikte tahmin eder.

### Adım 4: zamansal tutarlılık testi

Eğitimden sonra bir video örnekleme yapın. Kareler arası farkı ölçün. Model zamansal yapıyı öğrendiyse, farklar her kareyi bağımsız örnekleme yapmaya kıyasla daha küçük kalır.

## Tuzaklar

- **Bağımsız kare bazlı örnekleme = titreme (flicker).** Her kareyi ayrı ayrı çalıştırırsanız, her karenin gürültüsü bağımsız olduğu için çıktı titrer. Video diffüzyonu, kareleri attention veya paylaşılan gürültüyle bağlayarak bunu çözer.
- **Naif 3D attention = bellek taşıması (OOM).** 10 saniyelik 1080p latent üzerinde tam 3D attention, yüzlerce milyar işlemdir. Uzamsal + zamansal olarak çarpanlayın.
- **Veri açıklama kalitesi boyuttan daha önemlidir.** Sora'nın önceki çalışmalara göre ana yükseltmesi, ~10 kat daha ayrıntılı açıklamayla eğitim almaktı (GPT-4 etiketli klipler). OpenAI'ın teknik raporu bunu açıkça belirtir.
- **İlk kare koşullandırması.** Üretim modellerinin çoğu bir görseli ilk kare olarak da kabul eder. Bu "görüntüden-videoya" modudur; eğitim bu varyantı da içerir.
- **Fizik sapması.** Uzun klipler (>10s) ince uyumsuzluklar biriktirir. Kayan pencere üretimi (sliding-window generation) + anahtar kare sabitleme (keyframe anchoring) yardımcı olur.

## Kullan

| Kullanım durumu | 2026 seçimi |
|----------------|-------------|
| En yüksek kaliteli metinden-videoya, barındırma | Veo 3 veya Sora |
| Kamera kontrollü sinematik | Motion brushes ile Runway Gen-3 |
| Klipler arası karakter tutarlılığı | Pika 2.0 veya Kling 2.1 |
| Açık ağırlıklar, hızlı fine-tune | WAN 2.2 + LoRA |
| Görüntüden-videoya | WAN 2.2-I2V, Kling 2.1 I2V veya Runway |
| Sesden-videoya dudak senkronizasyonu | Veo 3 (doğal ses) veya özel dudak senkronizasyonu modeli |
| Video düzenleme | Runway Act-Two, Kling Motion Brush, Flux-Kontext (durgun kare) |

Kalite eşitliğinde videonun saniye başına maliyeti 2024 ile 2026 arasında 20 kat düştü.

## Teslim Et

`outputs/skill-video-brief.md` dosyasını kaydedin. Skill bir video brifingi (süre, en-boy oranı, stil, kamera planı, konu tutarlılığı, ses) alır ve çıktı olarak şunları verir: model + barındırma, iskelet prompt (kamera dili, konu açıklaması, hareket tanımlayıcıları), seed + tekrarlanabilirlik protokolü ve kare-düzeyinde QA kontrol listesi.

## Alıştırmalar

1. **Kolay.** `code/main.py`'de (a) bağımsız kare bazlı örnekleme ve (b) birlikte dizi örnekleme için kareler arası farkı karşılaştırın. Farkların ortalamasını ve varyansını raporlayın.
2. **Orta.** İlk kare koşulunu ekleyin: 0. kareyi belirli bir değere sabitleyin ve geri kalanını örnekleme yapın. Sabitlenmiş değerin nasıl yayıldığını ölçün.
3. **Zor.** HuggingFace diffusers ile yerel bir GPU'da CogVideoX-2B çalıştırın. 6 saniyelik bir klip için 720p'de 20 çıkarım adımı zamanlayın. Uzamsal-zamansal attention'ı profilleyerek darboğazı belirleyin.

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| Video VAE | "3D VAE" | `(T, H, W, C)` → uzamsal-zamansal latent sıkıştıran encoder. |
| Yamalar | "Token'lar" | Latent'ın sabit boyutlu 3 boyutlu blokları; DiT'in girdisi. |
| Çarpanlı attention | "Uzamsal + zamansal" | Önce uzayda, sonra zamanda attention çalıştırın; tam 3D attention'ı atlayın. |
| Görüntüden-videoya (I2V) | "Bu fotoğrafı canlandır" | Model bir görsel + metin alır, ondan başlayan bir video üretir. |
| Anahtar kare koşullandırması | "Sabit kareler" | Videonun akışını kontrol etmek için belirli kareleri sabitleyin. |
| Hareket fırçası | "Yönlü ipucu" | Kullanıcının hareket vektörlerini görsel üzerine çizdiği girdi. |
| Yeniden açıklama | "Yoğun açıklamalar" | Eğitim kliplerini ayrıntılı promptlarla yeniden etiketlemek için LLM kullanma. |
| Titreme | "Zamansal bozulma" | Kareler arası uyumsuzluk; bağlı gürültü temizlemeyle düzeltilir. |

## Üretim notu: video latent'leri bant genişliği sorunudur

10 saniyelik 1080p klip, 24 fps'de 240 kare × 1920 × 1080 × 3 ≈ 1.5 GB ham pikseldir. 4× video VAE sıkıştırmasından (`2 × uzamsal × 2 × zamansal`) sonra latent, istek başına ~100 MB'dur. Bunu batch 1'de 30 adım boyunca bir uzamsal-zamansal DiT üzerinden çalıştırırsanız, HBM üzerinden adım başına ~3 GB/veri transferi yaparsınız — darboğaz FLOP değil bant genişliğidir.

Üç üretim ayarı, doğrudan üretim-çıkarım literatüründen:

- **DiT üzerinde TP.** Metinden-videoya modelleri rutin olarak ≥10B parametredir. 4 H100 üzerinde TP=4 standarttır; 405B sınıfı modeller için PP=2 × TP=2. Adım başına gecikme, TP ile all-reduce duvarına kadar yaklaşık doğrusal olarak düşer.
- **Kare gruplaması = continuous batching.** Üretim zamanında video kavramsal olarak attention ile bağlı bir kare grubudur. Continuous batching (sflight zamanlaması) uygulanır: kare `t-1` döndürülürken kare `t+1`'i render etmeye başlayın, eğer model mimarisi kayan pencere üretimine izin veriyorsa.
- **Klip düzeyinde doldurma önbelleği (prefill cache).** Görüntüden-videoya için ilk kare koşullandırması, bir LLM'in prompt doldurmasına benzer: bir kez hesaplayın, zamansal decoder geçişleri boyunca yeniden kullanın. Bu, video için bir KV-önbelleğidir (KV-cache).

## Daha Fazla Kaynak

- [Brooks ve ark. (2024). Video generation models as world simulators](https://openai.com/index/video-generation-models-as-world-simulators/) — Sora teknik raporu.
- [Yang ve ark. (2024). CogVideoX: Text-to-Video Diffusion Models with An Expert Transformer](https://arxiv.org/abs/2408.06072) — CogVideoX.
- [Kong ve ark. (2024). HunyuanVideo: A Systematic Framework for Large Video Generative Models](https://arxiv.org/abs/2412.03603) — HunyuanVideo.
- [Genmo (2024). Mochi-1 Technical Report](https://www.genmo.ai/blog/mochi) — Mochi-1.
- [Alibaba (2025). WAN 2.2](https://wanvideo.io/) — 2025 ortasında açık SOTA.
- [Ho, Salimans, Gritsenko ve ark. (2022). Video Diffusion Models](https://arxiv.org/abs/2204.03458) — çığır açan video diffüzyon makalesi.
- [Blattmann ve ark. (2023). Align your Latents (Video LDM)](https://arxiv.org/abs/2304.08818) — Stable Video Diffusion'in atası.
