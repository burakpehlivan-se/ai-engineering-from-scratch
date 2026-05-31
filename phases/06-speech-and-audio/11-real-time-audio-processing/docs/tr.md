# Gerçek Zamanlı Ses İşleme

> Toplu (batch) hatları bir dosyayı işler. Gerçek zamanlı hatlar bir sonraki 20 milisaniyeyi, bir sonraki 20 milisaniye gelmeden önce işler. Her konuşma yapay zekası, yayın stüdyosu ve telefon botu bu gecikme bütçesinde yaşar veya ölür.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 6 · 02 (Spektrogramlar), Faz 6 · 04 (ASR), Faz 6 · 07 (TTS)
**Süre:** ~75 dakika

## Problem

Canlı hissettiren bir ses asistanı istiyorsunuz. İnsan konuşması sıralama gecikmesi (turn-taking latency) ~230 ms'dir (sessizlikten yanıtına). 500 ms'nin üstü robotik hissettirir; 1500 ms'nin üstü bozuk hissettirir. 2026'da tam bir **dinle → anla → yanıt ver → konuş** döngüsü için bütçe:

| Aşama | Bütçe |
|-------|-------|
| Mikrofon → tampon | 20 ms |
| VAD | 10 ms |
| ASR (akışlı) | 150 ms |
| LLM (ilk token) | 100 ms |
| TTS (ilk parça) | 100 ms |
| Sesanlatıcı → hoparlör | 20 ms |
| **Toplam** | **~400 ms** |

Moshi (Kyutai, 2024) 200 ms tam çift taraflı (full-duplex) hızına ulaştı. GPT-4o-realtime (2024) ~320 ms hızındadır. 2022'deki kademeli hatlar 2500 ms ile gönderilmişti. 10× iyileşme üç tekniğten geldi: (1) her yerde akış, (2) kısmi sonuçlarla asenkron boru hattı, (3) kesilebilir üretim.

## Kavram

![Halka tamponlu, VAD kapılı, kesintili akışlı ses hattı](../assets/real-time.svg)

**Kare / parça / pencere.** Gerçek zamanlı ses sabit boyutlu bloklar halinde akar. Yaygın seçim: 20 ms (16 kHz'de 320 örnek). Aşağıdaki her şey bu tempoya ayak uydurmalıdır.

**Halka tamponu (ring buffer).** Sabit boyutlu dairesel tampon. Üretici ipliği yeni kareleri yazar, tüketici ipliği okur. Sıcak yol (hot path) boyunca tahsisleri engeller. Boyut = maksimum gecikme × örnekleme hızı; 2 saniyelik 16 kHz halka = 32.000 örnek.

**VAD (Ses Aktivitesi Algılama).** Kimse konuşmadığında aşağı akım işini kapar. Silero VAD 4.0 (2024) CPU'da 30 ms kare başına <1 ms çalışır. `webrtcvad` daha eski alternatiftir.

**Akışlı ASR.** Ses geldikçe kısmi transkripsiyonlar çıkaran modeller. Parakeet-CTC-0.6B akışlı modda (NeMo, 2024) 320 ms gecikmede %2–5 WER yapar. Whisper-Streaming (Macháček ve ark., 2023) Whisper'ı ~2 s gecikmeyle neredeyse akışlı hale getirir.

**Kesme (interruption).** Kullanıcı asistan konuşurken konuştuğunda (a) araya girmeyi (barge-in) algılamalı, (b) TTS'yi durdurmalı, (c) kalan LLM çıktısını atmalısınız. 100 ms içinde, aksi halde kullanıcı sağır asistan hisseder.

**WebRTC Opus aktarımı.** 20 ms kareler, 48 kHz, uyarlanabilir bit hızı 8–128 kbps. Tarayıcı ve mobil için standart. LiveKit, Daily.co, Pion 2026'da ses uygulamaları için kullanılan yığınlardır.

**Titresim tamponu (jitter buffer).** Ağ paketleri sırasız / geç gelir. Titresim tamponu yeniden sıralar ve yumuşatır; çok küçük → duyulabilir boşluklar, çok büyük → gecikme. 60–80 ms tipik.

### Yaygın tuzaklar

- **İplik rekabeti.** Python'un GIL'i + ağır modeller ses ipliğini aç bırakabilir. C-geri aramalı ses kitaplığı (sounddevice, PortAudio) kullanın ve Python'u sıcak yolun dışında tutun.
- **Örnekleme hızı dönüştürme gecikmesi.** Hattın içinde yeniden örnekleme 5–20 ms ekler. Ya baştan yeniden örnekleme yapın ya da sıfır gecikmeli yeniden örnekleme (PolyPhase, `soxr_hq`) kullanın.
- **TTS hazırlama.** Kokoro gibi hızlı TTS bile ilk istekte 100–200 ms ısınma süresi tutar. Modeli önbelleğe alın ve ilk gerçek turdan önce sahte bir çalıştırma ile ısıtın.
- **Yankı giderme (echo cancellation).** AEC olmadan, TTS çıktısı mikrofona geri girer ve bot'un kendi sesi üzerinde ASR tetikler. WebRTC AEC3 açık kaynak varsayılanıdır.

## İnşa Et

### Adım 1: halka tamponu

```python
import collections

class RingBuffer:
    def __init__(self, capacity):
        self.buf = collections.deque(maxlen=capacity)
    def write(self, frame):
        self.buf.extend(frame)
    def read(self, n):
        return [self.buf.popleft() for _ in range(min(n, len(self.buf)))]
    def level(self):
        return len(self.buf)
```

#### Açıklama
Kapasite maksimum tamponlama gecikmesini belirler. 16 kHz'de 32.000 örnek = 2 s.

### Adım 2: VAD kapısı

```python
def simple_energy_vad(frame, threshold=0.01):
    return sum(x * x for x in frame) / len(frame) > threshold ** 2
```

#### Açıklama
Üretimde Silero VAD ile değiştirin:

```python
import torch
vad, _ = torch.hub.load("snakers4/silero-vad", "silero_vad")
is_speech = vad(torch.tensor(frame), 16000).item() > 0.5
```

### Adım 3: akışlı ASR

```python
# Parakeet-CTC-0.6B NeMo aracılığıyla akışlı
from nemo.collections.asr.models import EncDecCTCModelBPE
asr = EncDecCTCModelBPE.from_pretrained("nvidia/parakeet-ctc-0.6b")
# chunk_ms=320 ms, look_ahead_ms=80 ms
for chunk in audio_stream():
    partial_text = asr.transcribe_streaming(chunk)
    print(partial_text, end="\r")
```

#### Açıklama
NeMo Parakeet-CTC modeliyle akışlı transkripsiyon yaparak kısmi metinleri gerçek zamanlı olarak yazdırır.

### Adım 4: kesme işleyicisi

```python
class Dialog:
    def __init__(self):
        self.tts_task = None

    def on_user_speech(self, frame):
        if self.tts_task and not self.tts_task.done():
            self.tts_task.cancel()   # araya girme
        # sonra akışlı ASR'ye besle

    def on_final_user_utterance(self, text):
        self.tts_task = asyncio.create_task(self.reply(text))

    async def reply(self, text):
        async for tts_chunk in llm_then_tts(text):
            speaker.write(tts_chunk)
```

#### Açıklama
Asenkron G/Ç ve iptal edilebilir TTS akışına dayanır. WebRTC peerconnection.stop() ses parçası üzerinde standart yoldur.

## Kullan

2026 yığını:

| Katman | Seçin |
|--------|-------|
| Aktarım | LiveKit (WebRTC) veya Pion (Go) |
| VAD | Silero VAD 4.0 |
| Akışlı ASR | Parakeet-CTC-0.6B veya Whisper-Streaming |
| LLM ilk-token | Groq, Cerebras, vLLM-streaming |
| Akışlı TTS | Kokoro veya ElevenLabs Turbo v2.5 |
| Yankı giderme | WebRTC AEC3 |
| Uçtan uca yerli | OpenAI Realtime API veya Moshi |

## Tuzaklar

- **Güvenli olmak için 500 ms tamponlama.** Tampon *gecikme zemininizdir*. Küçültün.
- **İplikleri sabitlememek.** Ses geri çağıracası (callback) öncelik-düşük iplikte = yük altında kırılmalar.
- **TTS parçaları çok küçük.** 200 ms altı parçalar vokoder bozukluklarını duyulabilir hale getirir. 320 ms parçalar en iyi noktadır.
- **Titresim tamponu yok.** Gerçek ağlar titreyicidir; yumuşatma olmadan patlamalar alırsınız.
- **Tek atışlı hata yönetimi.** Ses hatları çökmeye karşı dayanıklı olmalıdır. Tek bir istisna oturumu öldürür.

## Gönder

`outputs/skill-realtime-designer.md` olarak kaydedin. Aşama başına somut gecikme bütçeleriyle gerçek zamanlı bir ses hattı tasarlayın.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Halka tamponu + enerji VAD'si simüle eder; sahte 10 saniyelik akış için aşama gecikmelerini yazdırır.
2. **Orta.** `sounddevice` kullanarak, mikrofonunuzu 20 ms karelere bölerek işleyen bir geçiş döngüsü (passthrough) oluşturun ve her karede VAD durumunu yazdırın.
3. **Zor.** `aiortc` ile tam çift taraflı bir yankı testi oluşturun: tarayıcı → WebRTC → Python → WebRTC → tarayıcı. 1 kHz darbe ile camdan-cama gecikmeyi ölçün.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|---------------------|------------------------|
| Halka tamponu | Dairesel kuyruk | Ses kareleri için sabit boyutlu, kilitssiz (veya SPSC-kilitli) FIFO. |
| VAD | Sessizlik kapısı | Konuşma ile konuşmayı olmayanı işaretleyen model veya sezgisel. |
| Akışlı ASR | Gerçek zamanlı STT | Ses geldikçe kısmi metin çıkarır; sınırlı ileriye bakış. |
| Titresim tamponu | Ağ yumuşatıcı | Sırasız paketleri yeniden sıralayan kuyruk; 60–80 ms tipik. |
| AEC | Yankı giderme | Hoparlörden mikrofona geri besleme yolunu çıkartır. |
| Araya girme | Kullanıcı kesme | Sistem TTS sırasında kullanıcı konuşmasını algılar; oynatmayı iptal etmeli. |
| Tam çift taraflı | Aynı anda her iki yönde | Kullanıcı ve bot aynı anda konuşabilir; Moshi tam çift taraflıdır. |

## İleri Okuma

- [Macháček ve ark. (2023). Whisper-Streaming](https://arxiv.org/abs/2307.14743) — parçalanmış neredeyse akışlı Whisper.
- [Kyutai (2024). Moshi](https://kyutai.org/Moshi.pdf) — tam çift taraflı 200 ms gecikme.
- [LiveKit Ajan çerçevesi (2024)](https://docs.livekit.io/agents/) — üretim düzeyinde ses ajanı orkestasyonu.
- [Silero VAD deposu](https://github.com/snakers4/silero-vad) — <1 ms VAD, Apache 2.0.
- [WebRTC AEC3 makalesi](https://webrtc.googlesource.com/src/+/main/modules/audio_processing/aec3/) — açık kaynakta yankı giderme.
