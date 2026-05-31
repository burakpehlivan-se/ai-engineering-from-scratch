# Ses Aktivitesi Algılama ve Sıralama — Silero, Cobra ve Flush Hilesi

> Her ses ajanı iki kararda yaşar veya ölür: kullanıcı şu an konuşuyor mu ve bitti mi? VAD ilkinе yanıt verir. Sıralama algılama (VAD + sessizlik geçiş süresi + anlamsal son-noktalama modeli) ikincisine yanıt verir. Yanlış yaparsanız ya kullanıcıları kesersiniz ya da hiç susmazsınız.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 6 · 11 (Gerçek Zamanlı Ses), Faz 6 · 12 (Ses Asistanı)
**Süre:** ~45 dakika

## Problem

Bir ses ajanının her 20 ms parçada aldığı üç farklı karar:

1. **Bu kare konuşma mı?** — VAD. İkili, kare bazlı.
2. **Kullanıcı yeni bir ifadeye başladı mı?** — başlangıç algılama (onset detection).
3. **Kullanıcı bitti mi?** — son-noktalama (end-pointing, tur sonu).

Saf cevap (enerji eşiği) herhangi bir gürültüde başarısız olur — trafik, klavyeler, kalabalık uğultusu. 2026 cevabı: Silero VAD (açık, derin öğrenmeli) + bir sıralama algılama modeli (anlamsal son-noktalama) + VAD-kalibreli sessizlik geçiş süresi.

## Kavram

![VAD kaskadı: enerji → Silero → sıralama algılayıcı → flush hilesi](../assets/vad-turn-taking.svg)

### Üç katmanlı VAD kaskadı

**1. Katman: enerji kapısı.** En ucuz. Eşik RMS -40 dBFS'de. Bariz sessizliği filtreler ama eşik üzerindeki herhangi bir gürültüde ateşlenir.

**2. Katman: Silero VAD** (2020-2026, MIT). 1M parametre. 6000+ dilde eğitilmiştir. Tek CPU ipliğinde 30 ms parçada ~1 ms çalışır. %5 FPR'de %87.7 TPR. Açık kaynak varsayılanı.

**3. Katman: anlamsal sıralama algılayıcı.** LiveKit'in sıralama algılama modeli (2024-2026) veya kendi küçük sınıflandırıcınız. "Cümle ortası duraklama"yı "konuşmayı bitirme"den ayırır. Yalnızca sessizlik değil, dilbilgisel bağlamı (tonlama + son kelimeler) kullanır.

### Anahtar parametreler ve varsayılanları

- **Eşik.** Silero bir olasılık çıkarır; konuşmayı > 0.5 (varsayılan) veya > 0.3 (hassas) ile sınıflandırın. Düşük eşik = daha az ilk kelime kırpması, daha fazla yanlış pozitif.
- **Minimum konuşma süresi.** 250 ms'den kısa konuşmayı reddedin — genellikle öksürük veya sandalye gürültüsü.
- **Sessizlik geçiş süresi (son-noktalama).** VAD 0'a döndükten sonra tur sonunu ilan etmeden önce 500-800 ms bekleyin. Çok kısa → kullanıcıyı keser. Çok uzun → yavaş hissettirir.
- **Hazırlık tamponu (pre-roll buffer).** VAD tetiklenmeden önce 300-500 ms ses tutun. "Hey" kelimesinin kırpılmasını önler.

### Flush hilesi (Kyutai 2025)

Akışlı STT modellerinin bir ileriye bakma gecikmesi vardır (Kyutai STT-1B için 500 ms, STT-2.6B için 2.5 s). Normalde konuşmanın bitiminden sonra transkripsiyon için o kadar beklersiniz. Flush hilesi: VAD konuşma sonunu tetiklediğinde, **STT'ye bir flush sinyali gönderin** ki anında çıktı versin. STT ~4× gerçek zamanlı hızında çalışır, bu yüzden 500 ms tampon ~125 ms'de biter.

Uçtan uca: 125 ms VAD + flush STT = konuşmacı gecikmesi.

### 2026 VAD karşılaştırması

| VAD | TPR @ %5 FPR | Gecikme | Lisans |
|-----|-------------|---------|--------|
| WebRTC VAD (Google, 2013) | %50.0 | 30 ms | BSD |
| Silero VAD (2020-2026) | %87.7 | ~1 ms | MIT |
| Cobra VAD (Picovoice) | %98.9 | ~1 ms | ticari |
| pyannote segmentasyonu | %95 | ~10 ms | MIT benzeri |

Silero doğru varsayılanıdır. Cobra uyumluluk / doğruluk yükseltmesidir. Yalnızca enerji tabanlı VAD'ın 2026 üretiminde yeri yoktur.

## İnşa Et

### Adım 1: enerji kapısı

```python
def energy_vad(chunk, threshold_dbfs=-40.0):
    rms = (sum(x * x for x in chunk) / len(chunk)) ** 0.5
    dbfs = 20.0 * math.log10(max(rms, 1e-10))
    return dbfs > threshold_dbfs
```

#### Açıklama
Kare üzerindeki ortalama karekök (RMS) enerjisini dBFS cinsinden hesaplar ve eşikle karşılaştırır.

### Adım 2: Python'da Silero VAD

```python
from silero_vad import load_silero_vad, get_speech_timestamps

vad = load_silero_vad()
audio = torch.tensor(waveform_16k, dtype=torch.float32)
segments = get_speech_timestamps(
    audio, vad, sampling_rate=16000,
    threshold=0.5,
    min_speech_duration_ms=250,
    min_silence_duration_ms=500,
    speech_pad_ms=300,
)
for s in segments:
    print(f"{s['start']/16000:.2f}s - {s['end']/16000:.2f}s")
```

#### Açıklama
Silero VAD'ı yükler ve ses dalgasındaki konuşma segmentlerini algılar.

### Adım 3: tur sonu durum makinesi

```python
class TurnDetector:
    def __init__(self, silence_hangover_ms=500, min_speech_ms=250):
        self.state = "idle"
        self.speech_ms = 0
        self.silence_ms = 0
        self.silence_hangover_ms = silence_hangover_ms
        self.min_speech_ms = min_speech_ms

    def update(self, is_speech, chunk_ms=20):
        if is_speech:
            self.speech_ms += chunk_ms
            self.silence_ms = 0
            if self.state == "idle" and self.speech_ms >= self.min_speech_ms:
                self.state = "speaking"
                return "START"
        else:
            self.silence_ms += chunk_ms
            if self.state == "speaking" and self.silence_ms >= self.silence_hangover_ms:
                self.state = "idle"
                self.speech_ms = 0
                return "END"
        return None
```

#### Açıklama
Konuşma ve sessizlik durumlarını izleyerek tur başlangıç ve bitiş sinyalleri üretir.

### Adım 4: flush hilesi iskeleti

```python
def flush_on_end(stt_client, audio_buffer):
    stt_client.send_audio(audio_buffer)
    stt_client.send_flush()
    return stt_client.recv_transcript(timeout_ms=150)
```

#### Açıklama
STT (Kyutai, Deepgram, AssemblyAI) bunun çalışması için flush desteği içermelidir. Whisper streaming buna destek vermez — parçalıdır ve her zaman parçaları bekler.

## Kullan

| Durum | VAD seçimi |
|-------|-----------|
| Açık, hızlı, genel | Silero VAD |
| Ticari çağrı merkezi | Cobra VAD |
| Cihaz üstü (telefon) | Silero VAD ONNX |
| Araştırma / diyarizasyon | pyannote segmentasyonu |
| Sıfır bağımlılıklı yedek | WebRTC VAD (eski) |
| Tur sonu kalitesi gerekli | Silero + LiveKit sıralama algılayıcı katmanlı |

Genel kural: gerçekten başka seçeneğiniz yoksa yalnızca enerji tabanlı VAD göndermeyin.

## Tuzaklar

- **Sabit eşik.** Sessiz ortamda çalışır, gürültülü ortamda başarısız olur. Ya cihaz üstünde kalibre edin ya da Silero'ya geçin.
- **Çok kısa sessizlik geçiş süresi.** Ajan cümle ortasında keser. Konuşmacı dili için 500-800 ms en iyi noktadır.
- **Çok uzun geçiş süresi.** Yavaş hissettirir. Hedef kullanıcılarla A/B testi yapın.
- **Hazırlık tamponu yok.** Kullanıcının ilk 200-300 ms sesi kaybolur. Her zaman kayan bir hazırlık tamponu tutun.
- **Anlamsal son-noktalamayı göz ardı etme.** "Hmm, bir düşüneyim..." uzun duraklamalar içerir. Kullanıcılar düşünce ortasında kesilmekten nefret eder. LiveKit'in sıralama algılayıcısını veya benzerini kullanın.

## Gönder

`outputs/skill-vad-tuner.md` olarak kaydedin. Bir iş yükü için VAD modeli, eşik, geçiş süresi, hazırlık ve sıralama stratejisini seçin.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Konuşma + sessizlik + konuşma + öksürük dizisini simüle eder ve üç VAD katmanını test eder.
2. **Orta.** `silero-vad`'ı kurun, 5 dakikalık bir kaydı işleyin, hem ilk kelime kırpımlarını hem de yanlış tetiklemeleri en aza indirmek için eşiği ayarlayın. Kesinlik/duyarlılığı raporlayın.
3. **Zor.** Küçük bir sıralama algılayıcı (turn-detector) inşa edin: Silero VAD + son 10 kelimenin gömmeleri üzerinde 3 katmanlı MLP (sentence-transformers kullanın). Elle etiketlenmiş bir tur sonu veri kümesi üzerinde eğitin. Yalnızca Silero'yu %10 F1 ile yenin.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|---------------------|------------------------|
| VAD | Konuşma dedektörü | Kare bazlı ikili: bu bir konuşma mı? |
| Sıralama algılama | Son-noktalama | VAD + sessizlik geçiş süresi + anlamsal son-nokta. |
| Sessizlik geçiş süresi | Konuşmadan sonra bekleme | Tur sonunu ilan etmeden önce bekleme süresi; 500-800 ms. |
| Hazırlık | Konuşma öncesi tampon | VAD tetiklenmeden önce 300-500 ms ses tutun. |
| Flush hilesi | Kyutai hilesi | VAD → flush-STT → 500 ms yerine 125 ms gecikme. |
| Anlamsal son-nokta | "Bitirmeyi amaçladılar mı?" | Yalnızca sessizliğe değil, kelimelere bakan ML sınıflandırıcısı. |
| TPR @ FPR %5 | ROC noktası | Standart VAD benchmark'ı; Silero %87.7, WebRTC %50. |

## İleri Okuma

- [Silero VAD](https://github.com/snakers4/silero-vad) — referans açık VAD.
- [Picovoice Cobra VAD](https://picovoice.ai/products/cobra/) — ticari doğruluk lideri.
- [Kyutai — Unmute + flush hilesi](https://kyutai.org/stt) — 200 ms altı mühendislik hilesi.
- [LiveKit — sıralama algılama](https://docs.livekit.io/agents/logic/turns/) — üretimde anlamsal son-noktalama.
- [WebRTC VAD](https://webrtc.googlesource.com/src/) — eski referans.
- [pyannote segmentasyonu](https://github.com/pyannote/pyannote-audio) — diyarizasyon düzeyinde segmentasyon.
