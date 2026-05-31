# Ses Anti-Spoofing ve Ses Filigranı — ASVspoof 5, AudioSeal, WaveVerify

> Ses klonlama savunmalardan daha hızlı gönderildi. 2026 üretim ses sistemlerinin iki şeye ihtiyacı var: gerçek ve sahte konuşmayı sınıflandıran bir dedektör (AASIST, RawNet2) ve sıkıştırmaya ve düzenlemeye dayanan bir filigran (audio watermark). İkisini birden gönderin veya ses klonlamasını göndermeyin.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 6 · 06 (Konuşmacı Tanıma), Faz 6 · 08 (Ses Klonlama)
**Süre:** ~75 dakika

## Problem

Birbiriyle ilişkili üç savunma:

1. **Anti-spoofing / deepfake algılama.** Verilen bir ses klibi, sentetik mi gerçek mi? ASVspoof benchmark'ları (ASVspoof 2019 → 2021 → 5) altın standarttır.
2. **Ses filigranı.** Üretilen sese fark edilemeyen bir sinyal yerleştirin ki bir dedektör daha sonra çıkarsın. AudioSeal (Meta) ve WavMark açık seçeneklerdir.
3. **Doğrulanmış menşe (authenticated provenance).** Ses dosyalarının + meta verilerinin kriptoografik imzası. C2PA / İçerik Özgünlüğü Girişimi (Content Authenticity Initiative).

Algılama işbirlikçi olmayan düşmanlarla başa çıkar. Filigran uyumlulukla başa çıkar — yapay zeka tarafından üretilen sesin这样 tanımlanması gerekir. 2026'da her ikisi de zorunludur.

## Kavram

![Anti-spoofing vs filigran vs menşe — üç savunma katmanı](../assets/spoofing-watermark.svg)

### ASVspoof 5 — 2024-2025 benchmark'ı

Önceki baskılardan en büyük değişiklik:

- **Kalabalık kaynaklı veri** (stüdyo temizliği değil) — gerçekçi koşullar.
- **~2000 konuşmacı** (önceki ~100'e kıyasla).
- **32 saldırı algoritması.** TTS + ses dönüştürme + düşmanca bozulma (adversarial perturbation).
- **İki iz.** Karşı tedbir (CM) bağımsız algılama; Spoofing-robust ASV (SASV) biyometrik sistemler için.

ASVspoof 5'te en iyi durum: ~%7.23 EER. Daha eski ASVspoof 2019 LA'de: %0.42 EER. Gerçek dünya dağıtımında: vahşi kliplerde %5-10 EER bekleyin.

### AASIST ve RawNet2 — algılama model aileleri

**AASIST** (2021, 2026'ya kadar güncellendi). Spektral özellikler üzerinde grafik dikkati (graph-attention). ASVspoof 5 karşı tedbir görevinde güncel SOTA.

**RawNet2.** Ham dalga formu üzerine konvolüsyonel ön uç + TDNN omurgası. Daha basit referans; ince ayarla hala rekabetçi.

**NeXt-TDNN + SSL özellikleri.** 2025 varyantı: ECAPA tarzı + WavLM özellikleri + odak kaybı (focal loss). ASVspoof 2019 LA'de %0.42 EER'ye ulaşır.

### AudioSeal — 2024 filigran varsayılanı

Meta'nın **AudioSeal**'i (Ocak 2024, v0.2 Aralık 2024). Temel tasarım:

- **Yerelleştirilmiş.** 16 kHz örnekleme çözünürlüğünde (1/16000 s) kare bazında filigranı tespit eder.
- **Üretici + dedektör birlikte eğitilir.** Üretici duyulamayan sinyal yerleştirmeyi; dedektör augmentasyonlardan bulmayı öğrenir.
- **Dayanıklı.** MP3 / AAC sıkıştırma, EQ, hız kayması ±10%, gürültü karışımı +10 dB SNR'a dayanır.
- **Hızlı.** Dedektör 485× gerçek zamanlı hızında çalışır; WavMark'dan 1000× daha hızlı.
- **Kapasite.** 16-bit yük (payload) (model kimliği, üretim zaman damgası, kullanıcı kimliği kodlanabilir) her ifadeye yerleştirilebilir.

### WavMark

AudioSeal öncesi açık referans. Tersine çevrilebilir sinir ağı, 32 bit/sn. Sorunlar:

- Senkronizasyon kaba kuvveti yavaş.
- Gauss gürültüsü veya MP3 sıkıştırmasıyla kaldırılabilir.
- Gerçek zamanlı dostu değil.

### WaveVerify (Temmuz 2025)

AudioSeal'ın zayıflıklarını ele alır — özellikle zamansal manipülasyonları (ters çevirme, hız). FiLM tabanlı üretici + Uzmanlar Karışımı (Mixture-of-Experts) dedektörü kullanır. Standart saldırılarda AudioSeal ile rekabetçi; zamansal düzenlemelerle başa çıkar.

### Düşmanların fırsata çevirdiği boşluk

AudioMarkBench'den: "perde kayması (pitch shift) altında, tüm filigranların Bit Kurtarma Doğruluğu 0.6'nın altında, neredeyse tamamen kaldırma anlamına geliyor." **Perde kayması evrensel saldırı.** 2026'da aggressif perde değişikliğine karşı tamamen dayanıklı bir filigran yoktur. Bu yüzden filigranla birlikte algılama (AASIST) gereklidir.

### C2PA / İçerik Özgünlüğü Girişimi

Bir ML tekniği değil — bir manifesto biçimi. Ses dosyaları oluşturma aracı, yazar, tarih hakkında kriptoografik imzalı meta veri taşır. Audobox / Seamless kullanır. Menşe için iyidir; kötü niyetli biri yeniden kodlayıp meta verileri çıkardığında hiçbir şey yapmaz.

## İnşa Et

### Adım 1: basit spektral özellik dedektörü (oyuncak)

```python
def spectral_rolloff(spec, percentile=0.85):
    cum = 0
    total = sum(spec)
    if total == 0:
        return 0
    threshold = total * percentile
    for k, v in enumerate(spec):
        cum += v
        if cum >= threshold:
            return k
    return len(spec) - 1

def is_suspicious(audio):
    spec = magnitude_spectrum(audio)
    rolloff = spectral_rolloff(spec)
    return rolloff / len(spec) > 0.92
```

#### Açıklama
Sentezlenmiş konuşma genellikle olağandışı düz yüksek frekans enerjisine sahiptir. Üretim dedektörleri AASIST kullanır, bunu değil. Ama sezgisel doğru çalışır.

### Adım 2: AudioSeal yerleştirme + tespit

```python
from audioseal import AudioSeal
import torch

generator = AudioSeal.load_generator("audioseal_wm_16bits")
detector = AudioSeal.load_detector("audioseal_detector_16bits")

audio = load_wav("generated.wav", sr=16000)[None, None, :]
payload = torch.tensor([[1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0]])
watermark = generator.get_watermark(audio, sample_rate=16000, message=payload)
watermarked = audio + watermark

result, decoded_payload = detector.detect_watermark(watermarked, sample_rate=16000)
# result: [0, 1] arası float — filigran varlığı olasılığı
# decoded_payload: 16 bit; yerleştirilmiş yükle eşleştirin
```

#### Açıklama
AudioSeal üreteci ile sese 16-bit filigran yerleştirir, dedektörle geri çıkartır.

### Adım 3: değerlendirme — EER

```python
def eer(real_scores, fake_scores):
    thresholds = sorted(set(real_scores + fake_scores))
    best = (1.0, 0.0)
    for t in thresholds:
        far = sum(1 for s in fake_scores if s >= t) / len(fake_scores)
        frr = sum(1 for s in real_scores if s < t) / len(real_scores)
        if abs(far - frr) < best[0]:
            best = (abs(far - frr), (far + frr) / 2)
    return best[1]
```

#### Açıklama
Gerçek ve sahte puanlar kümesi üzerinde Eşit Hata Oranı (EER) hesaplar.

### Adım 4: üretim entegrasyonu

```python
def safe_tts(text, voice, clone_reference=None):
    if clone_reference is not None:
        verify_consent(user_id, clone_reference)
    audio = tts_model.synthesize(text, voice)
    audio_with_wm = audioseal_embed(audio, payload=build_payload(user_id, model_id))
    manifest = c2pa_sign(audio_with_wm, user_id, timestamp=now())
    return audio_with_wm, manifest
```

#### Açıklama
Her üretim: (1) filigran, (2) imzalı manifest, (3) saklama politikası uyumlu denetim kaydı gönderir.

## Kullan

| Kullanım alanı | Savunma |
|---------------|---------|
| TTS / ses klonlama gönderme | Her çıktıya AudioSeal yerleştirme (zorunlu) |
| Biyometrik ses kilidi | AASIST + ECAPA ensambli; canlılık meydan okuması |
| Çağrı merkezi dolandırıcılık algılama | Gelen çağrıların %20'sinde AASIST |
| Podcast özgünlüğü | Yüklemede C2PA imzası, yapay zeka üretilmişse AudioSeal |
| Araştırma / dedektör eğitimi | ASVspoof 5 train/dev/eval kümeleri |

## Tuzaklar

- **Filigran, dedektör asla çalıştırılmadan.** Anlamsız. CI'nizde dedektörü gönderin.
- **Kalibrasyonsuz algılama.** AASIST, ASVspoof LA üzerinde eğitilerek aşırı uyum (overfitting) yapar; gerçek dünya doğruluğu düşer. Kendi alanınızda kalibre edin.
- **Perde kayması boşluğu.** Agresif perde kayması大多数 filigranı kaldırır. Bir algılama yedeğiniz olsun.
- **Meta veri çıkarıp yeniden barındırma.** C2PA yeniden kodlamayla kolayca atlatılabilir. Her zaman kriptoografik + algısal (filigran) savunmayı birlikte ekleyin.
- **Canlılık olarak algılama.** Kullanıcıdan rastgele bir cümle söylemesini isteyin. Yeniden oynatma saldırılarını önler ama gerçek zamanlı klonlamayı önlemez.

## Gönder

`outputs/skill-spoof-defender.md` olarak kaydedin. Bir ses üretimi dağıtımı için algılama modeli, filigran, menşe manifestosu ve operasyonel rehberi seçin.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Sentezel ses üzerinde oyuncak dedektör + oyuncak filigran yerleştirme/tespiti.
2. **Orta.** `audioseal`'ı kurun, bir TTS çıktısına 16-bit yük yerleştirin, yeniden çıkartın. Sesi gürültüyle bozulayın ve Bit Kurtarma Doğruluğunu ölçün.
3. **Zor.** ASVspoof 2019 LA üzerinde RawNet2 veya AASIST ile ince ayar yapın. EER'yi ölçün. Ayrılmış F5-TTS üretilmiş klipler kümesinde test edin — OOD algılamasının ne kadar bozulduğuna bakın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|---------------------|------------------------|
| ASVspoof | Benchmark | İki yılda bir düzenlenen meydan okuma; 2024 = ASVspoof 5. |
| CM (karşı tedbir) | Dedektör | Sınıflandırıcı: gerçek konuşma vs sentetik / dönüştürülmüş. |
| SASV | Konuşmacı doğrulama + CM | Entegre biyometrik + spoof algılama. |
| AudioSeal | Meta filigranı | Yerelleştirilmiş, 16-bit yük, WavMark'dan 485× daha hızlı. |
| Bit Kurtarma Doğruluğu | Filigran dayanıklılığı | Saldırıdan sonra kurtarılan yük bit oranı. |
| C2PA | Menşe manifestosu | Oluşturma / yazarlık hakkında kriptoografik meta veri. |
| AASIST | Dedektör ailesi | Grafik dikkat tabanlı anti-spoofing SOTA'sı. |

## İleri Okuma

- [Todisco et al. (2024). ASVspoof 5](https://dl.acm.org/doi/10.1016/j.csl.2025.101825) — güncel benchmark.
- [Defossez et al. (2024). AudioSeal](https://arxiv.org/abs/2401.17264) — filigran varsayılanı.
- [Chen et al. (2025). WaveVerify](https://arxiv.org/abs/2507.21150) — Zamansal saldırılar için MoE dedektörü.
- [Jung et al. (2022). AASIST](https://arxiv.org/abs/2110.01200) — SOTA algılama omurgası.
- [AudioMarkBench (2024)](https://proceedings.neurips.cc/paper_files/paper/2024/file/5d9b7775296a641a1913ab6b4425d5e8-Paper-Datasets_and_Benchmarks_Track.pdf) — dayanıklılık değerlendirmesi.
- [C2PA teknik şartnamesi](https://c2pa.org/specifications/specifications/) — menşe manifestosu biçimi.
