# Ses Üretimi (Audio Generation)

> Ses, 16-48 kHz'de bir 1-D sinyaldir. Beş saniyelik bir klip 80-240k örnektir. Hiçbir transformer bu diziyi doğrudan dikkate almaz. 2026'daki her üretim ses modelinin çözümü aynıdır: bir sinirsel codec (Encodec, SoundStream, DAC) sesi 50-75 Hz'de ayrık token'lara sıkıştırır ve bir transformer veya diffüzyon modeli token'ları üretir.

**Tür:** İnşa Et
**Diller:** Python
**Ön koşullar:** Faz 6 · 02 (Ses Özellikleri), Faz 6 · 04 (ASR), Faz 8 · 06 (DDPM)
**Süre:** ~45 dakika

## Problem

Üç ses üretimi görevi:

1. **Metinden-sese (TTS).** Verilen metin, konuşma üretir. Temiz konuşma dar bantlıdır ve güçlü fonetik yapıya sahiptir — transformer-over-tokens tarafından iyi çözülür. VALL-E (Microsoft), NaturalSpeech 3, ElevenLabs, OpenAI TTS.
2. **Müzik üretimi.** Verilen bir prompt (metin, melodi, akor ilerlemesi, tür), müzik üretir. Çok daha geniş dağılım. MusicGen (Meta), Stable Audio 2.5, Suno v4, Udio, Riffusion.
3. **Ses efektleri / ses tasarımı.** Verilen bir prompt, ambiyans sesi veya foley üretir. AudioGen, AudioLDM 2, Stable Audio Open.

Üçü de aynı altyapı üzerinde çalışır: sinirsel ses codec'i + token-AR veya diffüzyon üreticisi.

## Kavram

![Ses üretimi: codec token'ları + transformer veya diffüzyon](../assets/audio-generation.svg)

### Sinirsel ses codec'leri

Encodec (Meta, 2022), SoundStream (Google, 2021), Descript Audio Codec (DAC, 2023). Evrişimli bir encoder dalgaformunu zaman adımına bir vektöre sıkıştırır; artımlı vektör nicemlemesi (RVQ) her vektörü K dizin indeksli sözlük kaskadına dönüştürür. Decoder tersini yapar. 24 kHz ses, 75 Hz'de 8 RVQ sözlüğü kullanarak 2 kbps'de = 600 token/saniye.

```
waveform (16000 samples/sec)
    └─ encoder conv ─┐
                     ├─ RVQ layer 1 → indices at 75 Hz
                     ├─ RVQ layer 2 → indices at 75 Hz
                     ├─ ...
                     └─ RVQ layer 8
```

#### Açıklama

RVQ'nin her katmanı bir öncekinin artık (residual) değerini modellemesi, sesin aşamalı olarak daha hassas bir şekilde kodlanmasını sağlar.

### Üzerinde iki üretici paradigma

**Token-otoregresif (token-autoregressive).** RVQ token'larını düzleştirip bir diziye dönüştürün, decoder-only bir transformer çalıştırın. MusicGen, K sözlük akışını akış-ofsetli paralel olarak "gecikmeli paralel" (delayed parallel) kullanarak üretir. VALL-E, bir metin promptundan + 3 saniyelik ses örneğinden konuşma token'ları üretir.

**Latent diffüzyon.** Codec token'larını sürekli (continuous) latent olarak paketleyin veya kategorik diffüzyonla modelleyin. Stable Audio 2.5, sürekli ses latent'leri üzerinde flow matching kullanır. AudioLDM 2, metinden-melodan-sesee diffüzyon kullanır.

2024-2026 eğilimi: müzik için flow matching kazanıyor (daha hızlı çıkarım, daha temiz örnekler), konuşma ise doğal olarak nedensel (causal) ve iyi akış sağladığı için token-AR hâlâ baskın.

## Üretim manzarası

| Sistem | Görev | Omurga | Gecikme |
|--------|-------|--------|---------|
| ElevenLabs V3 | TTS | Token-AR + sinirsel vocoder | ~300ms ilk token |
| OpenAI GPT-4o audio | Tam çift yönlü konuşma | Uçtan uca multimodal AR | ~200ms |
| NaturalSpeech 3 | TTS | Latent flow matching | Akışsız |
| Stable Audio 2.5 | Müzik / SFX | DiT + ses latent'leri üzerinde flow matching | 1 dakika klip için ~10s |
| Suno v4 | Tam şarkılar | Açıklanmamış; token-Şüpheli | Şarkı başına ~30s |
| Udio v1.5 | Tam şarkılar | Açıklanmamış | Şarkı başına ~30s |
| MusicGen 3.3B | Müzik | Encodec 32kHz üzerinde token-AR | Gerçek zamanlı |
| AudioCraft 2 | Müzik + SFX | Flow matching | 5s klip için ~5s |
| Riffusion v2 | Müzik | Spektrogram diffüzyonu | ~10s |

## İnşa Et

`code/main.py` temel fikri simüle eder: iki farklı "stilden" (stil A için alternasyonlu düşük ve yüksek token'lar, stil B için monoton rampa) üretilen sentetik "ses token" dizileri üzerinde küçük bir next-token transformer eğitir. Stille koşullandırın ve örnekleme yapın.

### Adım 1: sentetik ses token'ları

```python
def make_tokens(style, length, vocab_size, rng):
    if style == 0:  # "speech-like": alternating
        return [i % vocab_size for i in range(length)]
    # "music-like": ramp
    return [(i * 3) % vocab_size for i in range(length)]
```

### Adım 2: küçük bir token tahmincisi eğitin

Stil ile koşullandırılmış bigram tarzı bir tahminci. Nokta şu: codec token'ları → çapraz entropy eğitimi → otoregresif örnekleme.

### Adım 3: koşullu örnekleme

Stil token'ı ve başlangıç token'ı verildiğinde, bir sonraki token'ı tahmin edilen dağılımdan örnekleme yapın. 20-40 token boyunca devam edin.

## Tuzaklar

- **Codec kalitesi çıktı kalitesini sınırlar.** Codec bir sesi sadakatle temsil edemiyorsa, üretici kalitesi ne olursa olsun yardımcı olmaz. DAC mevcut en iyi açık codec'tir.
- **RVQ hata birikimi.** Her RVQ katmanı bir öncekinin artık değerini modellemesi nedeniyle, 1. katmandaki hatalar yayılır. Daha yüksek katmanlarda sıcaklık (temperature) 0 ile örnekleme yardımcı olur.
- **Müzik yapısı.** 30 saniyelik token, 75 Hz'de 20k+ tokendır. Transformer'lar için zor. Musicgen kayan pencere + prompt devamı kullanır; Stable Audio daha kısa klipler + geçişli harmanlama (crossfading) kullanır.
- **Sınır bozulmaları.** Üretilmiş klipler arasında geçişli harmanlama, dikkatli bir üst üste bindirme (overlap-add) gerektirir.
- **Temiz veri iştahı.** Müzik üreteçleri on binlerce saat lisanslı müzik gerektirir. Suno / Udio RIAA davası (2024) bunu gündeme getirdi.
- **Ses klonlama etiği.** 3 saniyelik bir örnek ve bir metin promptu, VALL-E / XTTS / ElevenLabs'ın bir sesi klonlaması için yeterlidir. Her üretim modeli kötüye kullanım tespiti + çıkış listeleri (opt-out lists) gerektirir.

## Kullan

| Görev | 2026 stack'i |
|-------|-------------|
| Ticari TTS | ElevenLabs, OpenAI TTS veya Azure Neural |
| Ses klonlama (onay doğrulanmış) | XTTS v2 (açık) veya ElevenLabs Pro |
| Arka plan müziği, hızlı | Stable Audio 2.5 API, Suno veya Udio |
| Sözli müzik | Suno v4 veya Udio v1.5 |
| Ses efektleri / foley | AudioCraft 2, ElevenLabs SFX veya Stable Audio Open |
| Gerçek zamanlı ses ajanı | GPT-4o realtime veya Gemini Live |
| Açık ağırlıklar müzik araştırması | MusicGen 3.3B, Stable Audio Open 1.0, AudioLDM 2 |
| Seslendirme / çeviri | HeyGen, ElevenLabs Dubbing |

## Teslim Et

`outputs/skill-audio-brief.md` dosyasını kaydedin. Skill bir ses brifingi (görev, süre, stil, ses, lisans) alır ve çıktı olarak şunları verir: model + barındırma, prompt formatı (tür etiketleri, stil tanımlayıcıları, yapısal işaretleyiciler), codec + üretici + vocoder zinciri, seed protokolü ve eval planı (MOS / CLAP skoru / TTS için CER / kullanıcı A/B testi).

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın ve stili açıkça ayarlayın. Üretilen dizilerin stilin kalıbıyla eşleştiğini doğrulayın.
2. **Orta.** Gecikmeli paralel decode ekleyin: 1 adım-ofsetli kalmak zorunda olan 2 token akışı simüle edin. Ortak bir tahminci eğitin.
3. **Zor.** HuggingFace transformers ile MusicGen-small'ı yerel olarak çalıştırın. Farklı üç prompt ile 10 saniyelik bir klip üretin; stil uyumu için A/B testi yapın.

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| Codec | "Sinirsel sıkıştırma" | Ses için encoder / decoder; tipik çıktı 50-75 Hz token'larıdır. |
| RVQ | "Artımlı VQ" | K nicemleyici (quantizer) kaskadı; her biri bir öncekinin artık değerini modeller. |
| Token | "Bir codec sembolü" | Sözlükteki ayrık indeks; tipik olarak 1024 veya 2048. |
| Gecikmeli paralel | "Ofsetli sözlükler" | Dizisizliği azaltmak için kademeli ofsetlerle K token akışı üretme. |
| Flow matching | "2024'ün ses kazananı" | Diffüzyona daha düz yollu alternatif; daha hızlı örnekleme. |
| Ses promptu | "3 saniyelik örnek" | Klonlanmış sesi yönlendiren konuşmacı embedding'i veya token ön ekisi. |
| Mel spektrogramı | "Görsel" | Log-büyüklük algısal spektrogramı; birçok TTS sistemi tarafından kullanılır. |
| Vocoder | "Mel'den dalgaya" | Mel spektrogramlarını sese geri dönüştüren sinirsel bileşen. |

## Üretim notu: ses bir akış (streaming) sorunudur

Ses, kullanıcıların *üretilirken* gelmesini beklediği çıkış modallitiesidir, hepsi bir arada değil. Üretim terimleriyle bu, TPOT'un (Çıktı Token'ı Başına Süre) önemli olduğu anlamına gelir, çünkü kullanıcının dinleme hızı hedef throughput'tur — okuma hızı değil. ~75 token/saniye (Encodec) ile tokenize edilmiş 16kHz ses için, sunucu oynatmayı akıcı tutmak için kullanıcı başına ≥75 token/saniye üretmelidir.

İki mimari sonuç:

- **Flow matching ses modelleri kolayca akış sağlayamaz.** Stable Audio 2.5 ve AudioCraft 2 sabit klip uzunluğunu bir geçişte render eder. Akış için klibi parçalara ayırır ve sınırları üst üste bindirir — kayan pencere diffüzyonu düşünün — codec AR modeline kıyasla 100-300ms gecikme ekler.

Ürün "canlı sesli sohbet" veya "gerçek zamanlı müzik devamı" ise, codec AR yolunu seçin. "Gönderildiğinde 30 saniyelik bir klip render etmek" ise, flow matching kalite ve toplam gecikmede kazanır.

## Daha Fazla Kaynak

- [Défossez ve ark. (2022). Encodec: High Fidelity Neural Audio Compression](https://arxiv.org/abs/2210.13438) — codec standartı.
- [Zeghidour ve ark. (2021). SoundStream](https://arxiv.org/abs/2107.03312) — ilk yaygın kullanılan sinirsel ses codec'i.
- [Kumar ve ark. (2023). High-Fidelity Audio Compression with Improved RVQGAN (DAC)](https://arxiv.org/abs/2306.06546) — DAC.
- [Wang ve ark. (2023). Neural Codec Language Models are Zero-Shot Text to Speech Synthesizers (VALL-E)](https://arxiv.org/abs/2301.02111) — VALL-E.
- [Copet ve ark. (2023). Simple and Controllable Music Generation (MusicGen)](https://arxiv.org/abs/2306.05284) — MusicGen.
- [Liu ve ark. (2023). AudioLDM 2: Learning Holistic Audio Generation with Self-supervised Pretraining](https://arxiv.org/abs/2308.05734) — AudioLDM 2.
- [Stability AI (2024). Stable Audio 2.5](https://stability.ai/news/introducing-stable-audio-2-5) — 2025 flow matching ile metinden-müziğe.
