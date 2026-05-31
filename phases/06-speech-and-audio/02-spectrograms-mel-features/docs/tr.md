# Spektrogramlar, Mel Ölçeği ve Ses Özellikleri

> Sinir ağları ham dalga şekillerini iyi tüketemez. Spektrogramları tüketirler. Mel spektrogramlarını daha da iyi tüketirler. 2026'daki her ASR, TTS ve ses sınıflandırıcısı bu tek ön işleme seçimine bağlı olarak yaşar veya ölür.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 6 · 01 (Ses Temelleri)
**Süre:** ~45 dakika

## Problem

10 saniyelik 16 kHz'lik bir kesik alın. Bu 160.000 float, hepsi `[-1, 1]` aralığında, "köpek havlıyor" veya "cat kelimesi" etiketiyle neredeyse hiç korele olmayan değerler. Ham dalga şekli bilgiyi içerir ama modelin kolayca çıkarabileceği bir formda değildir. 100 ms arayla söylenen iki özdeş ses tamamen farklı ham örneklere sahiptir.

Bir spektrogram bunu çözer. İnsan algısının görmezden geldiği zamansal ayrıntıyı çökertir (mikrosaniye titreşimi) ve algının dikkat ettiği yapıyı korur (hangi frekansların enerjik olduğu, ~10–25 ms'lik zaman pencerelerinde).

Mel spektrogramları daha da ileri gider. İnsanlar perdeyi logaritmik algılar: 100 Hz ile 200 Hz arasındaki fark, 1000 Hz ile 2000 Hz arasındaki farkla "aynı mesafe" gibi gelir. Mel ölçeği frekans eksenini buna göre eğir. Mel ölçekli spektrogram, 2010'dan 2026'ya kadar konuşma makine öğrenmesinin en önemli tek özelliğidir.

## Kavram

![Dalga şeklinden STFT'ye, mel spektrogramdan MFCC merdivenine](../assets/mel-features.svg)

**STFT (Kısa Süreli Fourier Dönüşümü).** Dalga şekline örtüşmeli çerçeveler dilimleyin (tipik: 25 ms pencere, 10 ms adım = 16 kHz'de 400 örnek / 160 örnek). Her çerçeveyi bir pencere fonksiyonuyla çarpın (varsayılan Hann'dır; Hamming biraz farklı takas). Her çerçeveyi FFT'ye sokun. Genlik spektrumlarını `(n_çerçeve, n_freksiyon_bin)` şeklinde bir matris olarak istifleyin. Bu sizin spektrogramınızdır.

**Logaritmik genlik.** Ham genlikler 5-6 mertebe genişliğindedir. Dinamik aralığı sıkıştırmak için `log(|X| + 1e-6)` veya `20 * log10(|X|)` alın. Her üretim hattı ham genlik değil, logaritmik genlik kullanır.

**Mel ölçeği.** `f` frekansı Hz cinsinden `m = 2595 * log10(1 + f / 700)` formülüyle mel'e eşlenir. Eşleme 1 kHz'in altında yaklaşık doğrusal, üstünde yaklaşık logaritmiktir. 0–8 kHz'i kapsayan 80 mel bin'i standart ASR girdisidir.

**Mel filtre bankası.** Mel ölçeğinde eşit aralıklı bir üçgen filtre seti. Her filtre komşu FFT bin'lerinin ağırlıklı toplamıdır. STFT genliğini filtre bankası matrisiyle çarpmak bir matmul ile mel spektrogramını verir.

**Log-mel spektrogram.** `log(mel_spec + 1e-10)`. Whisper'ın girdisi. Parakeet'in girdisi. SeamlessM4T'nin girdisi. 2026'nın evrensel ses ön yüzü.

**MFCC'ler.** Log-mel spektrogramı alın, DCT (tip II) uygulayın, ilk 13 katsayıyı tutun. Özellikleri dekore eder ve daha fazla sıkıştırır. 2015 civarına kadar baskın özellikti; CNN'ler/Transformer'lar ham log-mel'lerde ona yetişti. Hala speaker recognition'da (x-vectors, ECAPA) kullanılır.

**Çözünürlük takası.** Daha büyük FFT = daha iyi frekans çözünürlüğü ama daha kötü zaman çözünürlüğü. 25 ms / 10 ms ses-ML varsayılanıdır; müzik için 50 ms / 12.5 ms; geçici algılama (davul vuruşları, plosifler) için 5 ms / 2 ms.

## İnşa Et

### Adım 1: dalga şeklini çerçevele

```python
def frame(signal, frame_len, hop):
    n = 1 + (len(signal) - frame_len) // hop
    return [signal[i * hop : i * hop + frame_len] for i in range(n)]
```

#### Açıklama
10 saniyelik 16 kHz'lik bir kesik `frame_len=400, hop=160` ile 998 çerçeve üretir.

### Adım 2: Hann penceresi

```python
import math

def hann(N):
    return [0.5 * (1 - math.cos(2 * math.pi * n / (N - 1))) for n in range(N)]
```

#### Açıklama
FFT öncesi nokta bazında çarpılır. Sıfır olmayan uç noktalarda kesilerek oluşan spektral sızıntıyı kaldırır.

### Adım 3: STFT genliği

```python
def stft_magnitude(signal, frame_len=400, hop=160):
    win = hann(frame_len)
    frames = frame(signal, frame_len, hop)
    return [magnitudes(dft([w * s for w, s in zip(win, f)])) for f in frames]
```

#### Açıklama
Üretimde `torch.stft` veya `librosa.stft` (FFT destekli, vektörlenmiş) kullanılır. Buradaki döngü öğretim amaçlıdır; `code/main.py` içinde kısa kliplerde çalışır.

### Adım 4: mel filtre bankası

```python
def hz_to_mel(f):
    return 2595.0 * math.log10(1.0 + f / 700.0)

def mel_to_hz(m):
    return 700.0 * (10 ** (m / 2595.0) - 1)

def mel_filterbank(n_mels, n_fft, sr, fmin=0, fmax=None):
    fmax = fmax or sr / 2
    mels = [hz_to_mel(fmin) + (hz_to_mel(fmax) - hz_to_mel(fmin)) * i / (n_mels + 1)
            for i in range(n_mels + 2)]
    hzs = [mel_to_hz(m) for m in mels]
    bins = [int(h * n_fft / sr) for h in hzs]
    fb = [[0.0] * (n_fft // 2 + 1) for _ in range(n_mels)]
    for m in range(n_mels):
        for k in range(bins[m], bins[m + 1]):
            fb[m][k] = (k - bins[m]) / max(1, bins[m + 1] - bins[m])
        for k in range(bins[m + 1], bins[m + 2]):
            fb[m][k] = (bins[m + 2] - k) / max(1, bins[m + 2] - bins[m + 1])
    return fb
```

#### Açıklama
0–8 kHz'i kapsayan 80 mel ile `n_fft=400` `(80, 201)` boyutunda bir matris üretir. `(n_çerçeve, 201)` STFT genliği transpozuyla çarpılarak `(n_çerçeve, 80)` mel spektrogramı elde edilir.

### Adım 5: log-mel

```python
def log_mel(mel_spec, eps=1e-10):
    return [[math.log(max(v, eps)) for v in frame] for frame in mel_spec]
```

#### Açıklama
Yaygın alternatifler: `librosa.power_to_db` (referans-normalize dB), `10 * log10(power + eps)`. Whisper daha karmaşık bir kırpma + normalize rutini kullanır (Whisper'ın `log_mel_spectrogram` fonksiyonuna bakın).

### Adım 6: MFCC'ler

```python
def dct_ii(x, n_coeffs):
    N = len(x)
    return [
        sum(x[n] * math.cos(math.pi * k * (2 * n + 1) / (2 * N)) for n in range(N))
        for k in range(n_coeffs)
    ]
```

#### Açıklama
Her log-mel çerçevesine DCT uygulayın, ilk 13 katsayıyı tutun. Bu sizin MFCC matrisinizdir. İlk katsayı genellikle düşürülür (toplam enerjiyi kodlar).

## Kullan

2026 yığını:

| Görev | Özellikler |
|------|-----------|
| ASR (Whisper, Parakeet, SeamlessM4T) | 80 log-mel, 10 ms adım, 25 ms pencere |
| TTS akustik modeli (VITS, F5-TTS, Kokoro) | 80 mel, ince zamansal kontrol için 5–12 ms adım |
| Ses sınıflandırma (AST, PANNs, BEATs) | 128 log-mel, 10 ms adım |
| Speaker embedding (ECAPA-TDNN, WavLM) | 80 log-mel veya ham dalga şekli SSL |
| Müzik (MusicGen, Stable Audio 2) | EnCodec ayrık jetonları (mel değil) |
| Anahtar kelime algılama | Küçük cihazlar için 40 MFCC |

Kural: **müzik üzerinde çalışmıyorsanız, 80 log-mel ile başlayın.** Sapmanın ispatı yükü-sizedır.

## 2026'da Hala Yaygınlaşan Tuzaklar

- **Mel sayısı uyumsuzluğu.** 80 mel ile eğitim, 128 mel ile çıkarım. Sessiz hata. Her iki uçta da özellik şeklini kaydedin.
- **Yukarı akış sampling rate uyumsuzluğu.** 22.05 kHz'de hesaplanan mel'ler 16 kHz'den farklı görünür. SR'yi özellik çıkarmadan önce düzeltin.
- **dB vs log.** Whisper log-mel bekler, dB-mel değil. Bazı HF hatları otomatik algılar; özel kodunuz algılamaz.
- **Normalizasyon kayması.** Eğitimde ifade başına normalizasyon, çıkarımda küresel normalizasyon. WER'yi ikiye katlayan üretim hatası.
- **Dolgudan sızıntı.** Bir klibin sonuna sıfır dolgu ekleme, sonraki çerçevelerde düz bir spektrum üretir. Simetrik doldurun veya çoğaltın.

## Gönder

`outputs/skill-feature-extractor.md` olarak kaydedin. Bu beceri, belirli bir model hedefi için özellik türünü, mel sayısını, çerçeve/adım ve normalizasyonu seçer.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Bir cırpı sentezler (frekans 200 → 4000 Hz之间 süpürür) ve çerçeve başına argmax mel bin'ini yazdırır. (İsteğe bağlı) çizin ve süpürmeyle eşleştiğini doğrulayın.
2. **Orta.** `n_mels` `{40, 80, 128}` ve `frame_len` `{200, 400, 800}` ile yeniden çalıştırın. Zaman ekseni boyunca keskin tepe bant genişliğini ölçün. Hangi kombinasyon cırpıları en iyi çözer?
3. **Zor.** `power_to_db` uygulayın ve AudioMNIST'te küçük bir CNN sınıflandırıcısının (a) ham log-mel, (b) `ref=max` ile dB-mel, (c) MFCC-13 + delta + delta-delta kullanarak ASR doğruluğunu karşılaştırın. top-1 doğruluğunu raporlayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|---------------------|------------------------|
| Çerçeve | Bir dilim | Bir FFT'ye beslenen 25 ms'lik dalga şekli parçası. |
| Adım | Adım | Ardışık çerçeveler arasındaki örnekler; 10 ms ASR varsayılanıdır. |
| Pencere | Hann/Hamming şeyi | Çerçeve kenarlarını sıfıra indirgeyen nokta bazlı çarpan. |
| STFT | Spektrogram üreteci | Çerçevelenmiş + pencerelenmiş FFT; zaman × frekans matrisi üretir. |
| Mel | Eğilmiş frekans | Logaritmik-algısal ölçek; `m = 2595·log10(1 + f/700)`. |
| Filtre bankası | Matris | STFT'yi mel bin'lerine projekte eden üçgen filtreler. |
| Log-mel | Whisper'ın girdisi | `log(mel_spec + eps)`; 2026'da standartlaştı. |
| MFCC | Eski usul özellik | Log-mel'in DCT'si; 13 katsayı, dekore edilmiş. |

## İleri Okuma

- [Davis, Mermelstein (1980). Comparison of parametric representations for monosyllabic word recognition](https://ieeexplore.ieee.org/document/1163420) — MFCC makalesi.
- [Stevens, Volkmann, Newman (1937). A Scale for the Measurement of the Psychological Magnitude Pitch](https://pubs.aip.org/asa/jasa/article-abstract/8/3/185/735757/) — Orijinal mel ölçeği.
- [OpenAI — Whisper source, log_mel_spectrogram](https://github.com/openai/whisper/blob/main/whisper/audio.py) — Referans uygulamayı okuyun.
- [librosa feature extraction docs](https://librosa.org/doc/main/feature.html) — `mfcc`, `melspectrogram` ve adım/pencere için referans.
- [NVIDIA NeMo — audio preprocessing](https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/main/asr/asr_all.html#featurizers) — Parakeet + Canary modelleri için üretim ölçekli hat.
