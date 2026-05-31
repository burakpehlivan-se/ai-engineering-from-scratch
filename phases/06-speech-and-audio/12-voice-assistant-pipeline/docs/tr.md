# Bir Ses Asistanı Hattı İnşa Etme — Faz 6 Bitirme Projesi

> Dersler 01-11'deki her şey bir araya getirildi. Dinleyen, akıl yürüten ve karşılık veren bir ses asistanı inşa edin. 2026'da bu çözülmüş bir mühendislik problemidir, araştırma problemi değil — ama entegrasyon detayları gönderip göndermediğinizi belirler.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 6 · 04, 05, 06, 07, 11; Faz 11 · 09 (Fonksiyon Çağırma); Faz 14 · 01 (Ajan Döngüsü)
**Süre:** ~120 dakika

## Problem

Uçtan uca bir asistan inşa edin:

1. Mikrofon girişini yakalar (16 kHz tek kanallı).
2. Kullanıcı konuşmasının başlangıcını/sonunu algılar.
3. Akışlı transkripsiyon yapar.
4. Transkripsiyonu araç çağırabilen (zamanlayıcı, hava durumu, takvim) bir LLM'ye aktarır.
5. LLM metnini bir TTS'ye aktarır.
6. Sesi kullanıcıya geri çalar.
7. Kullanıcı yanıt ortasında keserse durur.

Gecikme hedefi: dizüstü bilgisayar CPU'sunda kullanıcının konuşmasını bitirmesinden itibaren 800 ms içinde ilk TTS ses baytı. Kalite hedefi: kaçırılmış kelime yok, sessizlikte hayal görülen altyazı yok, ses klonlama sızıntısı yok, istem enjeksiyonu (prompt injection) başarıya ulaşamaz.

## Kavram

![Ses asistanı hattı: mikrofon → VAD → STT → LLM+araçlar → TTS → hoparlör](../assets/voice-assistant.svg)

### Yedi bileşen

1. **Ses yakalama.** Mikrofon → 16 kHz tek kanallı → 20 ms parçalar. Genellikle Python'da `sounddevice` veya üretimde yerel AudioUnit/ALSA/WASAPI.
2. **VAD (Ders 11).** Silero VAD @ eşik 0.5, minimum konuşma 250 ms, sessizlik geçiş süresi 500 ms. "Başlangıç" ve "bitiş" sinyalleri verir.
3. **Akışlı STT (Ders 4-5).** Whisper-streaming, Parakeet-TDT veya Deepgram Nova-3 (API). Kısmi + nihai transkripsiyonlar.
4. **Araç çağırmalı LLM.** GPT-4o / Claude 3.5 / Gemini 2.5 Flash. Araçlar için JSON şeması. Token'ları akıtın.
5. **Akışlı TTS (Ders 7).** Kokoro-82M (en hızlı açık kaynak) veya Cartesia Sonic (ticari). 20 LLM token'ından sonra TTS'yi başlatın.
6. **Oynatma.** Hoparlör çıkışı; düşük bant genişlikli ağlar için opus kodlayın.
7. **Kesme işleyicisi.** TTS oynatması sırasında VAD tetiklenirse oynatmayı durdurun, LLM'yi iptal edin, STT'yi yeniden başlatın.

### Karşılaşacağınız üç hata modu

1. **İlk kelime kırpılması.** VAD biraz geç başlar. Kullanıcının "hey" kelimesi eksik kalır. Başlangıç eşiğini 0.3'e ayarlayın, 0.5'e değil.
2. **Yanıt ortası kesme karışıklığı.** LLM kullanıcı kesintisinden sonra üretmeye devam eder; asistan kullanıcıyla aynı anda konuşur. VAD → LLM-iptal bağlantısını kurun.
3. **Sessizlik hayal görmesi.** Whisper, sessiz ısınma karelerinde "İzlediğiniz için teşekkürler" çıkarır. Her zaman VAD kapısı kullanın.

### 2026 üretim referans yığınları

| Yığın | Gecikme | Lisans | Notlar |
|-------|---------|--------|-------|
| LiveKit + Deepgram + GPT-4o + Cartesia | 350-500 ms | ticari API | 2026 sektör varsayılanı |
| Pipecat + Whisper-streaming + GPT-4o + Kokoro | 500-800 ms | çoğunlukla açık | Kendin-yap dostu |
| Moshi (tam çift taraflı) | 200-300 ms | CC-BY 4.0 | Tek model; farklı mimari, Ders 15 |
| Vapi / Retell (yönetilen) | 300-500 ms | ticari | En hızlı başlatma; sınırlı özelleştirme |
| Whisper.cpp + llama.cpp + Kokoro-ONNX | çevrimdışı | açık | Gizlilik / kenar |

## İnşa Et

### Adım 1: parçalı mikrofon yakalama (sözde kod)

```python
import sounddevice as sd

def mic_stream(chunk_ms=20, sr=16000):
    q = queue.Queue()
    def cb(indata, frames, time, status):
        q.put(indata.copy().flatten())
    with sd.InputStream(channels=1, samplerate=sr, blocksize=int(sr * chunk_ms/1000), callback=cb):
        while True:
            yield q.get()
```

#### Açıklama
Mikrofon ses akışından 20 ms'lik parçalar halinde örnek yakalayan bir üreteç (generator) fonksiyonu.

### Adım 2: VAD kapılı tur yakalama

```python
def capture_turn(stream, vad, pre_roll_ms=300, silence_ms=500):
    buf, pre, triggered = [], collections.deque(maxlen=pre_roll_ms // 20), False
    silent = 0
    for chunk in stream:
        pre.append(chunk)
        if vad(chunk):
            if not triggered:
                buf = list(pre)
                triggered = True
            buf.append(chunk)
            silent = 0
        elif triggered:
            silent += 20
            buf.append(chunk)
            if silent >= silence_ms:
                return b"".join(buf)
```

#### Açıklama
VAD'nin konuşma başlangıcını algılamasını bekler, konuşma sırasında kareleri toplar ve sessizlik süresi dolduğunda turu sonlandırır.

### Adım 3: akışlı STT → LLM → TTS

```python
async def turn(audio_bytes):
    transcript = await stt.transcribe(audio_bytes)
    async for token in llm.stream(transcript):
        async for audio in tts.stream(token):
            await speaker.play(audio)
```

#### Açıklama
Ses baytlarını transkripsiyona, transkripsiyonu LLM token'larına, token'ları ses parçalarına dönüştüren asenkron boru hattı.

### Adım 4: LLM döngüsü içinde araç çağırma

```python
tools = [
    {"name": "get_weather", "parameters": {"location": "string"}},
    {"name": "set_timer", "parameters": {"seconds": "int"}},
]

async for chunk in llm.stream(user_text, tools=tools):
    if chunk.type == "tool_call":
        result = dispatch(chunk.name, chunk.args)
        continue_streaming(result)
    if chunk.type == "text":
        await tts.stream(chunk.text)
```

#### Açıklama
LLM'in araç çağrısı JSON'u göndermesini,arbeitmenin (dispatcher) ilgili fonksiyonu çalıştırmasını ve sonucun LLM'e geri beslenmesini sağlar.

### Adım 5: kesme işleme

```python
tts_task = asyncio.create_task(tts_loop())
while True:
    chunk = await mic.get()
    if vad(chunk):
        tts_task.cancel()
        await speaker.stop()
        await new_turn()
        break
```

#### Açıklama
VAD konuşma algıladığında mevcut TTS görevini iptal eder, hoparlörü durdurur ve yeni bir tur başlatır.

## Kullan

Tüm yedi bileşeni bir araya getiren çalıştırılabilir bir simülasyon için `code/main.py`'ye bakın; donanım olmadan bile hattın şeklini görebilirsiniz. Gerçek uygulama için stub'ları şunlarla değiştirin:

- `silero-vad` (`pip install silero-vad`)
- `deepgram-sdk` veya `openai-whisper`
- `openai` (`gpt-4o`) veya `anthropic`
- `kokoro` veya `cartesia`
- `sounddevice` (G/Ç için)

## Tuzaklar

- **PII'yi sonsuza kadar kaydetme.** Tam tur sesi çoğu yargı alanında Kişisel Olarak Tanımlanabilir Bilgi (PII)'dir. 30 gün saklama, depolamada şifreli.
- **Araya girme yok.** Kullanıcılar kesintiye uğratacaktır. Asistanınızın konuşmayı durdurması gerekir.
- **Engelleyen TTS.** Senkron TTS olay döngüsünü engeller. Asenkron veya ayrı bir iplik kullanın.
- **Araç çağırma hatası yönetimi yok.** Araçlar başarısız olur. LLM hatayı alıp bir kez yeniden denemeli, sonra zarifçe düşüş yapmalıdır.
- **Aşırı titiz hayal görme filtreleri.** Aşırı filtreleme ve asistan "Bu konuda yardım edemem" der. Yetersiz filtreleme ve her şeyi söyler. Ayrılmış bir kümede kalibre edin.
- **Uyanma kelimesi seçeneği yok.** Sürekli dinleme bir gizlilik riskidir. Bir uyanma kelimesi kapısı ekleyin (Porcupine veya openWakeWord).

## Gönder

`outputs/skill-voice-assistant-architect.md` olarak kaydedin. Bütçe + ölçek + dil + uyum kısıtlamaları verildiğinde, tam bir yığın teknik şartnamesi üretin.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Stub modüllerle uçtan uca tam bir turu simüle eder ve aşama başına gecikmeyi yazdırır.
2. **Orta.** STT stub'ını önceden kaydedilmiş bir `.wav` üzerinde gerçek bir Whisper modeliyle değiştirin. WER ve uçtan uca gecikmeyi ölçün.
3. **Zor.** Araç çağırma ekleyin: `get_weather` (herhangi bir API) ve `set_timer` uygulayın. LLM'i araçlar üzerinden yönlendirin ve kullanıcı "5 dakikalık bir zamanlayıcı ayarla" dediğinde doğru fonksiyonun çalıştığını ve sözlü yanıtın onu doğruladığını doğrulayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|---------------------|------------------------|
| Tur | Kullanıcı + asistan round-trip'i | Bir VAD-kısıtlı kullanıcı konuşması + bir LLM-TTS yanıtı. |
| Araya girme | Kesme | Asistan konuşurken kullanıcı konuşur; asistan durur. |
| Uyanma kelimesi | "Hey asistan" | Kısa anahtar kelime dedektörü; Porcupine, Snowboy, openWakeWord. |
| Son-noktalama | Tur bitişi | Kullanıcının bitirdiğine dair VAD + minimum-sessizlik kararı. |
| Hazırlık | Konuşma öncesi tampon | VAD tetiklenmeden önce 200-400 ms ses tutun, ilk kelime kırpılmasını önler. |
| Araç çağırması | Fonksiyon çağrısı | LLM JSON çıkarır; çalışma zamanı yollar; sonuç döngü içinde geri beslenir. |

## İleri Okuma

- [LiveKit — ses ajanı başlangıç kılavuzu](https://docs.livekit.io/agents/) — üretim düzeyinde referans.
- [Pipecat — ses ajanı örnekleri](https://github.com/pipecat-ai/pipecat) — kendin-yap dostu çerçeve.
- [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime) — yönetilen ses-yerli yol.
- [Kyutai Moshi](https://github.com/kyutai-labs/moshi) — tam çift taraflı referans (Ders 15).
- [Porcupine uyanma kelimesi](https://picovoice.ai/products/porcupine/) — uyanma kelimesi kapısı.
- [Anthropic — araç kullanım kılavuzu](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) — LLM fonksiyon çağırma.
