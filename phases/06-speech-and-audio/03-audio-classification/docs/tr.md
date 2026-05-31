# Sınıflandırma — MFCC'lerde k-NN'den AST ve BEATs'e

> "Köpek havlama vs siren"den "bu hangi dil"e kadar her şey ses sınıflandırmasıdır. Özellikler mel'lerdir. Mimari her on yılda değişir. Değerlendirme ise AUC, F1 ve sınıf bazında recall olarak kalır.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 6 · 02 (Spektrogramlar & Mel), Faz 3 · 06 (CNN'ler), Faz 5 · 08 (Metin için CNN'ler ve RNN'ler)
**Süre:** ~75 dakika

## Problem

10 saniyelik bir kesik var. Şunu bilmek istiyorsunuz: "bu ne?" Kentsel ses (siren, matkap, köpek), konuşma komutu (evet/hayır/dur), dil kimliği (en/es/ar), konuşmacı duygusu (kızgın/nötr) veya çevresel ses (iç mekan/dış mekan, uğultu). Tümü *ses sınıflandırması*dır ve 2026'da temel mimari olgunlaşmıştır: log-mel → CNN veya Transformer → softmax.

Temel zorluk ağ değil. Veridir. Ses veri setlerinde acımasız sınıf dengesizliği, güçlü alan kayması (temiz vs gürültülü) ve etiket gürültüsü ("kentsel uğultu" ile "restoran gürültüsü"ne kim karar verdi?) vardır. Problemin %80'i veri seti oluşturma, artırma ve değerlendirmedir; CNN'yi Transformer ile değiştirmek değildir.

## Kavram

![Ses sınıflandırma merdiveni: MFCC'lerde k-NN'den AST'ye, BEATs'e](../assets/audio-classification.svg)

**MFCC'lerde k-NN (1990'lar temeli).** Her klipte MFCC'leri düzleştirin, etiketli bir bankaya kosinüs benzerliği hesaplayın, en yüksek K'nın çoğunluk oylamasını döndürün. Temiz, küçük veri setlerinde (Speech Commands, ESC-50) şaşırtıcı derecede güçlüdür. GPU olmadan çalışır.

**Log-mel'lerde 2D CNN (2015-2019).** `(T, n_mels)` log-meli bir görüntü gibi düşünün. ResNet-18 veya VGG tarzı uygulayın. Zaman ekseninde küresel ortalama havuzlama. Sınıflar üzerinde softmax. Hala 2026 kaggle yarışmalarının çoğunda temeldir.

**Audio Spectrogram Transformer, AST (2021-2024).** Log-meli yamalayın (ör. 16×16 yama), konum katmanları ekleyin, ViT'ye besleyin. Denetimli öğrenmede AudioSet'te en iyi durum (mAP 0.485).

**BEATs ve WavLM-base (2024-2026).** Milyonlarca saat üzerinde öz-denetimli ön eğitim. Görevinizde gerekecek denetimli verinin %1-10'unu kullanarak ince ayar yapın. 2026'da konuşma dışı ses için varsayılan başlangıç noktası budur. BEATs-iter3, AudioSet'te AST'yi 1-2 mAP yenerken hesaplamanın 1/4'ünü kullanır.

**Dondurulmuş omurga olarak Whisper encoder (2024).** Whisper'ın encoder'ını alın, decoder'ı bırakın, bir lineer sınıflandırıcı ekleyin. Dil kimliği ve basit olay sınıflandırmasında SOTA'ya yakın, sıfır ses artırımıyla. "Ücretsiz yemek" temeli.

### Sınıf dengesizliği gerçek zorluktur

ESC-50: 50 sınıf, her biri 40 klip — dengeli, kolay. UrbanSound8K: 10 sınıf, 10:1 dengesiz. AudioSet: 100.000:1 uzun kuyruklu 632 sınıf. İşe yarayan teknikler:

- Eğitimde dengeli örnekleme (değerlendirmede değil).
- Mixup: iki klibi (ve etiketlerini) doğrusal olarak ara değerle artırma olarak.
- Spektrum-Artırma (SpecAugment): rastgele zaman ve frekans bantlarını maskeleyin. Basit; kritik.

### Değerlendirme

- Çoklu sınıf tek etiketli (Speech Commands): top-1 doğruluğu, top-5 doğruluğu.
- Çoklu sınıf çoklu etiketli (AudioSet, UrbanSound tarzı): ortalama ortalama hassasiyet (mAP).
- Şiddetli dengesizlik: sınıf bazında recall + makro F1.

2026'da bilmeniz gereken sayılar:

| Benchmark | Temel | SOTA 2026 | Kaynak |
|-----------|-------|-----------|--------|
| ESC-50 | %82 (AST) | %97.0 (BEATs-iter3) | BEATs makalesi (2024) |
| AudioSet mAP | 0.485 (AST) | 0.548 (BEATs-iter3) | HEAR liderlik tablosu 2026 |
| Speech Commands v2 | %98 (CNN) | %99.0 (Audio-MAE) | HEAR v2 sonuçları |

## İnşa Et

### Adım 1: özellik çıkarımı

```python
def featurize_mfcc(signal, sr, n_mfcc=13, n_mels=40, frame_len=400, hop=160):
    mag = stft_magnitude(signal, frame_len, hop)
    fb = mel_filterbank(n_mels, frame_len, sr)
    mels = apply_filterbank(mag, fb)
    log = log_transform(mels)
    return [dct_ii(frame, n_mfcc) for frame in log]
```

#### Açıklama
Ham sinyali MFCC özelliklerine dönüştürür. STFT genliği, mel filtre bankası ve DCT uygulanarak 13 boyutlu özellik vektörleri elde edilir.

### Adım 2: sabit uzunlukta özet

```python
def summarize(mfcc_frames):
    n = len(mfcc_frames[0])
    mean = [sum(f[i] for f in mfcc_frames) / len(mfcc_frames) for i in range(n)]
    var = [
        sum((f[i] - mean[i]) ** 2 for f in mfcc_frames) / len(mfcc_frames) for i in range(n)
    ]
    return mean + var
```

#### Açıklama
Basit ama güçlü: zaman boyunca ortalama + varyans, 13 katsayılı MFCC için 26 boyutlu sabit bir embedding verir. Anında çalışır. 2017'ye kadar ESC-50'de en iyi durumdaki NN temellerini yenmiştir.

### Adım 3: k-NN

```python
def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1e-12
    nb = math.sqrt(sum(x * x for x in b)) or 1e-12
    return dot / (na * nb)

def knn_classify(q, bank, labels, k=5):
    sims = sorted(range(len(bank)), key=lambda i: -cosine(q, bank[i]))[:k]
    votes = Counter(labels[i] for i in sims)
    return votes.most_common(1)[0][0]
```

#### Açıklama
Kosinüs benzerliği hesaplanır, en yakın k komşu bulunur ve çoğunluk oylamasıyla sınıflandırma yapılır.

### Adım 4: log-mel'lerde CNN'e yükseltme

PyTorch'ta:

```python
import torch.nn as nn

class AudioCNN(nn.Module):
    def __init__(self, n_mels=80, n_classes=50):
        super().__init__()
        self.body = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
        )
        self.head = nn.Linear(128, n_classes)

    def forward(self, x):  # x: (B, 1, T, n_mels)
        return self.head(self.body(x).flatten(1))
```

#### Açıklama
3M parametre. Tek bir RTX 4090 ile ESC-50'de ~10 dakikada eğitilir. %80+ doğruluk.

### Adım 5: 2026 varsayılanı — BEATs ince ayarı

```python
from transformers import ASTFeatureExtractor, ASTForAudioClassification

ext = ASTFeatureExtractor.from_pretrained("MIT/ast-finetuned-audioset-10-10-0.4593")
model = ASTForAudioClassification.from_pretrained(
    "MIT/ast-finetuned-audioset-10-10-0.4593",
    num_labels=50,
    ignore_mismatched_sizes=True,
)

inputs = ext(audio, sampling_rate=16000, return_tensors="pt")
logits = model(**inputs).logits
```

#### Açıklama
AST modeli Transfer Learning ile 50 sınıfafine-tune edilir. BEATs için `microsoft/BEATs-base` `beats` kütüphanesiyle kullanılır; transformers API'si aynı şekildedir.

## Kullan

2026 yığını:

| Durum | Başlangıç |
|-------|----------|
| Küçük veri seti (<1000 klip) | MFCC ortalamalarında k-NN (temeliniz) + ses artırımı |
| Orta veri seti (1K–100K) | BEATs veya AST ince ayarı |
| Büyük veri seti (>100K) | Sıfırdan eğitim veya Whisper-encoder ince ayarı |
| Gerçek zamanlı, kenar | 40-MFCC CNN, int8'e nicellenmiş (KWS tarzı) |
| Çoklu etiketli (AudioSet) | BCE kaybı + mixup + SpecAugment ile BEATs-iter3 |
| Dil kimliği | MMS-LID, SpeechBrain VoxLingua107 temeli |

Karar kuralı: **taze bir modelle değil, dondurulmuş bir omurgayla başlayın.** BEATs başını ince ayar yapmak SOTA'nın %95'ini saatler içinde, haftalar içinde değil verir.

## Gönder

`outputs/skill-classifier-designer.md` olarak kaydedin. Belirli bir ses sınıflandırma görevi için mimariyi, artırımları, sınıf dengeleme stratejisini ve değerlendirme metriğini seçin.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. 4 sınıflı sentetik bir veri setinde (farklı perdelarda saf tonlar) k-NN MFCC temelini eğitir. Karışıklık matrisini raporlayın.
2. **Orta.** `summarize`'ı [ortalama, varyans, çarpıklık, basıklık] ile değiştirin. 4-moment havuzlaması aynı sentetik veri setinde ortalama+varyansı yener mi?
3. **Zor.** `torchaudio` kullanarak ESC-50 kat 1'de 2D CNN eğitin. 5 katlı çapraz doğrulama doğruluğunu raporlayın. SpecAugment (zaman maskesi = 20, frekans maskesi = 10) ekleyin ve farkı raporlayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|---------------------|------------------------|
| AudioSet | Sesin ImageNet'i | Google'ın 2M-klip, 632-sınıf zayıf etiketli YouTube veri seti. |
| ESC-50 | Küçük sınıflandırma benchmark'ı | 50 sınıf × 40 klip çevresel ses. |
| AST | Audio Spectrogram Transformer | Log-mel yamalarında ViT; 2021 SOTA. |
| BEATs | Öz-denetimli ses | Microsoft modeli, 2026 itibarıyla AudioSet'i liderliğinde. |
| Mixup | Çift artırma | `x = λ·x1 + (1-λ)·x2; y = λ·y1 + (1-λ)·y2`. |
| SpecAugment | Maske tabanlı artırma | Spektrogramın rastgele zaman ve frekans bantlarını sıfırla. |
| mAP | Ana çoklu etiket metriği | Sınıflar ve eşikler boyunca ortalama ortalama hassasiyet. |

## İleri Okuma

- [Gong, Chung, Glass (2021). AST: Audio Spectrogram Transformer](https://arxiv.org/abs/2104.01778) — 2021–2024 arası kayıtlı mimari.
- [Chen et al. (2022, rev. 2024). BEATs: Audio Pre-Training with Acoustic Tokenizers](https://arxiv.org/abs/2212.09058) — 2024+ varsayılanı.
- [Park et al. (2019). SpecAugment](https://arxiv.org/abs/1904.08779) — Baskın ses artırımı.
- [Piczak (2015). ESC-50 dataset](https://github.com/karolpiczak/ESC-50) — 50 sınıf benchmark'ı yaşamaya devam ediyor.
- [Gemmeke et al. (2017). AudioSet](https://research.google.com/audioset/) — 632 sınıf YouTube taksonomisi; hala altın standart.
