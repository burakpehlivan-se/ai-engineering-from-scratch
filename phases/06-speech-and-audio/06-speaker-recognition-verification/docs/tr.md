# Konuşmacı Tanıma ve Doğrulama

> ASR "ne söylendiğini" sorar. Konuşmacı tanıma "kimin söylediğini" sorar. Matematik aynı görünür — embedding'ler ve kosinüs — ama her üretim kararı tek bir EER sayısına bağlıdır.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 6 · 02 (Spektrogramlar & Mel), Faz 5 · 22 (Embedding Modelleri)
**Süre:** ~45 dakika

## Problem

Bir kullanıcı bir parola söyler. Şunu bilmek istiyorsunuz: bu kişi iddia ettiği kişi mi (*doğrulama*, 1:1), yoksa kayıt bankanızdaki ilk kişi mi (*kimlik tespiti*, 1:N)? Ya da hiçbiri — bilinmeyen bir konuşmacı mı (*açık küme*)?

2018 öncesi: GMM-UBM + i-vektörleri. Makul EER ama kanal kaymasına (telefon vs dizüstü) ve duyguya karşı kırılgan. 2018–2022: x-vektörleri (açısal marjin ile eğitilmiş TDNN omurgası). 2022+: ECAPA-TDNN ve WavLM-large embedding'leri. 2026'ya kadar alan üç model ve bir metrik tarafından domine edilmektedir.

Metrik **EER**'dir — Eşit Hata Oranı. Karar eşik False Accept Rate = False Reject Rate olacak şekilde ayarlanır. Kesişim noktası EER'dir. Her makalede, her liderlik tablosunda, her satın alma çağrısında kullanılır.

## Kavram

![Kayıt + doğrulama hattı: embedding + kosinüs + EER](../assets/speaker-verification.svg)

**Hat.** Kayıt: hedef konuşmacının 5–30 saniyesini kaydedin; sabit boyutlu bir embedding hesaplayın (ECAPA-TDNN için 192-boyut, WavLM-large için 256-boyut). Doğrulama: test ifadesinin embedding'ini alın; kosinüs benzerliği hesaplayın; bir eşikle karşılaştırın.

**ECAPA-TDNN (2020, 2026'da hala baskın).** Kanal Dikkatini Vurgulayan, Yayılım ve Birleştirme - Zaman Gecikmeli Sinir Ağı. Sıkıştırma-uzaklaştırma, çoklu dikkat havuzlaması ile 1D konvolüsyon blokları, ardından 192-boyuta lineer katman. VoxCeleb 1+2 (2.700 konuşmacı, 1.1M ifade) üzerinde Ekli Açısal Marjin kaybı (AAM-softmax) ile eğitilmiştir.

**WavLM-SV (2022+).** Önceden eğitilmiş WavLM-large SSL omurgasını AAM kaybıyla ince ayar yapın. Daha yüksek kalite ama daha yavaş — 300+ MB'ye karşı 15 MB.

**x-vector (temel).** TDNN + istatistik havuzlaması. Klasik; CPU/kenarda hala yararlı.

**AAM-softmax.** Doğru sınıf için `cos(θ + m)` ile doğru sınıfta açısal alana eklenmiş marjin `m` ile standart softmax. Sınıflar arası açısal ayrımı zorlar. Tipik `m=0.2`, ölçek `s=30`.

### Puanlama

- **Kosinüs** — kayıt ve test embedding'leri arasında. Eşik tabanlı karar.
- **PLDA (Olasılıksal LDA).** Embedding'leri, aynı konuşmacı ile farklı konuşmacı arasında kapalı form olasılık oranına sahip bir gizli alana projekte eder. Kosinüs üzerine eklenerek +10–20% EER azalması sağlar. 2020 öncesi standart; şimdi yalnızca kapalı küme kurulumlarında kullanılır.
- **Puan normalizasyonu.** `S-norm` veya `AS-norm`: her puanı taklitçi ortalamaları ve std'leri against normalize eder. Çapraz alan değerlendirmesi için gereklidir.

### Bilmeniz gereken sayılar (2026)

| Model | VoxCeleb1-O EER | Parametre | Verim (A100) |
|-------|-----------------|-----------|-------------|
| x-vector (klasik) | %3.10 | 5 M | 400× RT |
| ECAPA-TDNN | %0.87 | 15 M | 200× RT |
| WavLM-SV large | %0.42 | 316 M | 20× RT |
| Pyannote 3.1 segmentasyon + embedding | %0.65 | 6 M | 100× RT |
| ReDimNet (2024) | %0.39 | 24 M | 100× RT |

### Diarizasyon

Çok konuşmacılı bir kesikte "kim ne zaman konuştu". Hat: VAD → segment → her segmenti embed et → kümele (yığınlama veya spektral) → sınırları düzleştir. Modern yığın: `pyannote.audio` 3.1, tek bir çağrıyla konuşmacı segmentasyonu + embedding + kümelemeyi bir araya getirir. 2026'da AMI'de SOTA DER ~%15'tir (2022'deki %23'ten düştü).

## İnşa Et

### Adım 1: MFCC istatistiklerinden oyuncak embedding

```python
def embed_mfcc_stats(signal, sr):
    frames = featurize_mfcc(signal, sr, n_mfcc=13)
    mean = [sum(f[i] for f in frames) / len(frames) for i in range(13)]
    std = [
        math.sqrt(sum((f[i] - mean[i]) ** 2 for f in frames) / len(frames))
        for i in range(13)
    ]
    return mean + std  # 26 boyutlu
```

#### Açıklama
SOTA'dan çok uzak — yalnızca öğretim amaçlı. `code/main.py` bunu sentetik konuşmacı verilerinde kanıt olarak kullanır.

### Adım 2: kosinüs benzerliği + eşik

```python
def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0

def verify(enroll, test, threshold=0.75):
    return cosine(enroll, test) >= threshold
```

#### Açıklama
Kayıt ve test embedding'leri arasındaki kosinüs benzerliği hesaplanır ve bir eşikle karşılaştırılarak kabul/reddedilir.

### Adım 3: benzerlik çiftlerinden EER

```python
def eer(same_scores, diff_scores):
    thresholds = sorted(set(same_scores + diff_scores))
    best = (1.0, 1.0, 0.0)  # (fa, fr, eşik)
    for t in thresholds:
        fr = sum(1 for s in same_scores if s < t) / len(same_scores)
        fa = sum(1 for s in diff_scores if s >= t) / len(diff_scores)
        if abs(fa - fr) < abs(best[0] - best[1]):
            best = (fa, fr, t)
    return (best[0] + best[1]) / 2, best[2]
```

#### Açıklama
(eer, eer'deki eşik) döndürür. Her ikisini de raporlayın.

### Adım 4: SpeechBrain ile üretim

```python
from speechbrain.pretrained import EncoderClassifier

clf = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb")

# kayıt: 3-5 temiz örneğin embedding'lerinin ortalaması
enroll = torch.stack([clf.encode_batch(load(x)) for x in enrollment_clips]).mean(0)
# doğrulama
score = clf.similarity(enroll, clf.encode_batch(load("test.wav"))).item()
verdict = score > 0.25   # ECAPA tipik eşiği; verilerinizde ayarlayın
```

#### Açıklama
SpeechBrain ECAPA-TDNN modelini yükler, 3-5 temiz örneğin embedding ortalamasını alır ve test sesiyle karşılaştırır.

### Adım 5: pyannote ile diarizasyon

```python
from pyannote.audio import Pipeline

pipe = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
diarization = pipe("meeting.wav", num_speakers=None)
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"{turn.start:.1f}–{turn.end:.1f}  {speaker}")
```

#### Açıklama
Pyannote 3.1 ile çok konuşmacılı ses kaydında kimin ne zaman konuştuğunu otomatik olarak tespit eder.

## Kullan

2026 yığını:

| Durum | Seçin |
|-------|------|
| Kapalı küme 1:1 doğrulama, kenar | ECAPA-TDNN + kosinüs eşiği |
| Açık küme doğrulama, bulut | WavLM-SV + AS-norm |
| Diarizasyon (toplantılar, podcast'ler) | `pyannote/speaker-diarization-3.1` |
| Anti-spoofing (yeniden oynatma / deepfake algılama) | AASIST veya RawNet2 |
| Küçük gömülü (KWS + kayıt) | Titanet-Small (NeMo) |

## Tuzaklar

- **Kanal uyumsuzluğu.** VoxCeleb (web videosu) üzerinde eğitilmiş model ≠ telefon görüşmesi sesi. Her zaman hedef kanalda değerlendirin.
- **Kısa ifadeler.** EER 3 saniyenin altında test sesiyle keskin şekilde bozulur.
- **Gürültülü kayıt.** Tek bir gürültülü kaydı anchoring zehirler. ≥3 temiz örnek kullanın ve ortalamasını alın.
- **Koşullar arası sabit eşik.** Her zaman hedef alandan ayrılmış bir geliştirme kümesinde eşik ayarlayın.
- **Normalize edilmemiş embedding'lerde kosinüs.** Önce L2-normalize edin; aksi halde genlik baskınlık kazanır.

## Gönder

`outputs/skill-speaker-verifier.md` olarak kaydedin. Modeli, kayıt protokolünü, eşik ayarlama planını ve dolandırıcılık önlemlerini seçin.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Sentetik "konuşmacılar" (farklı ton profilleri) oluşturur, kaydeder, 100 çiftlik bir deneme listesinde EER hesaplar.
2. **Orta.** SpeechBrain ECAPA'yı 30 VoxCeleb1 ifadesi (5 konuşmacı × 6'şar) üzerinde kullanın. Kosinüs ile PLDA karşılaştırmalı EER hesaplayın.
3. **Zor.** `pyannote.audio` ile tam kaydet → diarize et → doğrula hattını oluşturun. AMI geliştirme kümesinde DER'yi değerlendirin.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|---------------------|------------------------|
| EER | Başlık metriği | False Accept = False Reject olan eşik. |
| Doğrulama | 1:1 | "Bu Alice mi?" |
| Kimlik tespiti | 1:N | "Kim konuşuyor?" |
| Açık küme | Bilinmeyen mümkün | Test kümesi kayıtsız konuşmacılar içerebilir. |
| Kayıt | Kayıt olma | Bir konuşmacının referans embedding'ini hesaplama. |
| AAM-softmax | Kayıp | Ekli açısal marjinli softmax; küme ayrımını zorlar. |
| PLDA | Klasik puanlama | Embedding'ler üzerinde olasılıksal LDA; olasılık oranlı puanlama. |
| DER | Diarizasyon metriği | Diarizasyon Hata Oranı — kaçırma + yanlış alarm + karışıklık. |

## İleri Okuma

- [Snyder et al. (2018). X-Vectors: Robust DNN Embeddings for Speaker Recognition](https://www.danielpovey.com/files/2018_icassp_xvectors.pdf) — Klasik derin embedding makalesi.
- [Desplanques et al. (2020). ECAPA-TDNN](https://arxiv.org/abs/2005.07143) — 2020–2026 arası baskın mimari.
- [Chen et al. (2022). WavLM: Large-Scale Self-Supervised Pre-Training for Full Stack Speech Processing](https://arxiv.org/abs/2110.13900) — SV ve diarizasyon için SSL omurgası.
- [Bredin et al. (2023). pyannote.audio 3.1](https://github.com/pyannote/pyannote-audio) — Üretim diarizasyon + embedding yığını.
- [VoxCeleb liderlik tablosu (2026'da güncellendi)](https://www.robots.ox.ac.uk/~vgg/data/voxceleb/) — Mevcut EER sıralamaları modeller genelinde.
