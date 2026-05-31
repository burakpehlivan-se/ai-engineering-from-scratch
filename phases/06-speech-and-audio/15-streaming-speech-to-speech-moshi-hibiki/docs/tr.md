# Akışlı Konuşmadan Konuşmaya — Moshi, Hibiki ve Tam Çift Taraflı Diyalog

> 2024-2026 ses yapay zekasını yeniden tanımladı. Moshi, 200 ms gecikmeyle aynı anda dinleyen ve konuşan tek bir model gönderir. Hibiki konuşma çevirmesini parça parça yapar. Her ikisi de ASR → LLM → TTS hattını terk eder ve Mimi codec token'ları üzerinde birleşik tam çift taraflı mimariye geçer. Bu yeni referans tasarımıdır.

**Tür:** Öğren
**Diller:** Python
**Ön koşullar:** Faz 6 · 13 (Nöral Ses Codec'leri), Faz 6 · 11 (Gerçek Zamanlı Ses), Faz 7 · 05 (Tam Transformer)
**Süre:** ~75 dakika

## Problem

Dersler 11 + 12'den inşa edilen her ses ajanının temel bir gecikme zemini (~300-500 ms) vardır: VAD ateşlenir, STT işler, LLM akıl yürütür, TTS üretir. Her aşamanın kendi minimum gecikmesi vardır. Ayarlayabilir ve paralelleştirebilirsiniz ama hattın şekli sizi sınırlar.

Moshi (Kyutai, 2024-2026) farklı bir soru sorar: eğer hat yoksa? Eğer bir model sesi alıp doğrudan, sürekli olarak ses çıkarırsa ve metin zorunlu bir aşama yerine aracılı "iç monolog" (inner monolog) olarak kullanılırsa?

Cevap **tam çift taraflı konuşmadan konuşmaya** (full-duplex speech-to-speech). Teorik gecikme 160 ms (80 ms Mimi karesi + 80 ms akustik gecikme). Tek L4 GPU'da pratik gecikme 200 ms. Bu, en iyi kademeli ses ajanının yarısıdır.

## Kavram

![Moshi mimarisi: iki paralel Mimi akışı + iç monolog metni](../assets/moshi-hibiki.svg)

### Moshi mimarisi

**Girdiler.** İki Mimi codec akışı, her ikisi de 12.5 Hz × 8 kod kitabı:

- Akış 1: kullanıcı sesi (Mimi-kodlanmış, sürekli gelen)
- Akış 2: Moshi'nin kendi sesi (Moshi tarafından üretilen)

**Transformer.** 7B parametreli Zamanlayıcı Transformer (Temporal Transformer) her iki akışı ve bir metin "iç monolog" akışını işler. Her 80 ms adımda:

1. En son kullanıcı Mimi token'larını tüketir (8 kod kitabı).
2. En son Moshi Mimi token'larını tüketir (8 kod kitabı, üretildiği haliyle).
3. Bir sonraki Moshi metin token'ını üretir (iç monolog).
4. Bir sonraki Moshi Mimi token'larını üretir (8 kod kitabı, küçük bir Derinlik Transformer'ı aracılığıyla).

Üç akış — kullanıcı sesi, Moshi sesi, Moshi metni — paralel çalışır. Moshi kullanıcıyı konuşurken duyabilir; kullanıcıkesintisinde kendini kesebilir; ana ifadesini bozmadan arka kanal ("hmm") yapabilir.

**Derinlik transformer'ı (depth transformer).** Bir kare içinde 8 kod kitabı paralel tahmin edilmez — kod kitabı arası bağımlılıkları vardır. 80 ms içinde küçük 2 katmanlı bir "derinlik transformer'ı" onları sırasıyla tahmin eder. Bu, AR codec LM'ler için standart ayrıştırmadır (VALL-E, VibeVoice tarafından da kullanılır).

### İç monolog metni neden yardımcı olur

Açık metin olmadan, model akustik akışında dili dolaylı olarak modellemek zorundadır. Moshi'nin içgörüsü: metin token'larını sesle birlikte çıkarmaya zorla. Metin akışı temelde Moshi'nin söylediklerinin transkripsiyonudur. Bu anlamsal tutarlılığı artırır, dil modeli başlığını (head) değiştirmeyi kolaylaştırır ve size ücretsiz transkripsiyonlar verir.

### Hibiki: akışlı konuşmadan konuşmaya çeviri

Aynı mimari, çeviri çiftleri üzerinde eğitilmiştir. Kaynak ses girer, hedef dil sesi sürekli olarak çıkar. Hibiki-Zero (Şubat 2026) kelimelerle hizalanmış eğitim verisi ihtiyacını ortadan kaldırır — cümle düzeyinde veri + gecikme optimizasyonu için GRPO pekiştirmeli öğrenme kullanır.

İlk olarak dört dil çifti desteklenir; ≈1000 saat ile yeni bir dile adapte edilebilir.

### Geniş Kyutai yığını (2026)

- **Moshi** — tam çift taraflı diyaloji (önce Fransızca, İngilizce iyi desteklenir)
- **Hibiki / Hibiki-Zero** — eş zamanlı konuşma çevirisi
- **Kyutai STT** — akışlı ASR (500 ms veya 2.5 s ileriye bakış)
- **Kyutai Pocket TTS** — 100M parametreli TTS CPU'da çalışır (Ocak 2026)
- **Unmute** — bunları birleştiren tam hat, sunucularda

L40S GPU'da verim: 3× gerçek zamanlı hızda 64 eş zamanlı oturum.

### Sesame CSM — kuzen

Sesame CSM (2025) benzer bir fikir kullanır — Mimi codec kafalı bir Llama-3 omurgası. Ama CSM tek yönlüdür (bağlam + metin alır, ses çıkarır), tam çift taraflı değildir. Pazardaki en iyi "ses mevcudiyeti" TTS'idir; Moshi'nin tam çift taraflı yeteneğiyle tam olarak aynı değildir.

### 2026 performans sayıları

| Model | Gecikme | Kullanım alanı | Lisans |
|-------|---------|---------------|--------|
| Moshi | 200 ms (L4) | tam çift taraflı İngilizce / Fransızca diyaloji | CC-BY 4.0 |
| Hibiki | 12.5 Hz kare hızı | Fransızca ↔ İngilizce akışlı çeviri | CC-BY 4.0 |
| Hibiki-Zero | aynı | 5 dil çifti, hizalanmış veri yok | CC-BY 4.0 |
| Sesame CSM-1B | 200 ms TTFA | bağlam koşullu TTS | Apache-2.0 |
| GPT-4o Realtime | ~300 ms | kapalı, OpenAI API | ticari |
| Gemini 2.5 Live | ~350 ms | kapalı, Google API | ticari |

## İnşa Et

### Adım 1: arayüz

Moshi, 80 ms'lik Mimi-kodlanmış ses parçaları alan ve her iki yönde sürekli olarak 80 ms'lik Mimi-kodlanmış ses parçaları döndüren bir WebSocket sunucusu sunar.

```python
import asyncio
import websockets
from moshi.client_utils import encode_audio_mimi, decode_audio_mimi

async def moshi_chat():
    async with websockets.connect("ws://localhost:8998/api/chat") as ws:
        mic_task = asyncio.create_task(stream_mic_to(ws))
        spk_task = asyncio.create_task(stream_from_to_speaker(ws))
        await asyncio.gather(mic_task, spk_task)
```

#### Açıklama
Moshi WebSocket sunucusuna bağlanarak mikrofondan ses gönderen ve hoparlöre ses alan iki asenkron görevi paralel çalıştırır.

### Adım 2: tam çift taraflı döngü

```python
async def stream_mic_to(ws):
    async for chunk_80ms in mic_stream_at_12_5_hz():
        mimi_tokens = encode_audio_mimi(chunk_80ms)
        await ws.send(serialize(mimi_tokens))

async def stream_from_to_speaker(ws):
    async for msg in ws:
        mimi_tokens, text_token = deserialize(msg)
        audio = decode_audio_mimi(mimi_tokens)
        await play(audio)
```

#### Açıklama
Her iki yön aynı anda çalışır. Python asyncio veya Rust futures standart aktarım olarak kullanılır.

### Adım 3: eğitim hedefi (kavramsal)

Her 80 ms kare `t` için:

- Girdi: `user_mimi[0..t]`, `moshi_mimi[0..t-1]`, `moshi_text[0..t-1]`
- Tahmin: `moshi_text[t]`, sonra `moshi_mimi[t, codebook_0..7]`

Metin sesten önce tahmin edilir (iç monolog); ses derinlik transformer'ı içinde kod kitabı sırasıyla tahmin edilir.

### Adım 4: Moshi'nin nerede kazandığı ve kazanmadığı

Moshi kazanır:

- Ucuza donanımda 250 ms altı uçtan uca.
- Doğal arka kanallar ve kesintiler.
- Hat yapıştırıcı (glue) kodu yok.

Moshi kazanmaz:

- Araç çağırması (eğitilmemiş; ayrı bir LLM yoluna ihtiyacınız var).
- Uzun akıl yürütme (Moshi ~8B diyaloji modelidir, Claude/GPT-4 değil).
- Niş konularda olgusal doğruluk.
- Çoğu kurumsal üretim kullanım alanı (2026'da hala hatlar kullanılır).

## Kullan

| Durum | Seçin |
|-------|-------|
| En düşük gecikmeli ses yoldaşı | Moshi |
| Canlı çeviri görüşmesi | Hibiki |
| Ses demosu / araştırma | Moshi, CSM |
| Araçlı kurumsal ajan | Hat (Ders 12), Moshi değil |
| Bağlamda özel sesli TTS | Sesame CSM |
| Konuşmadan konuşmaya, her dil | GPT-4o Realtime veya Gemini 2.5 Live (ticari) |

## Tuzaklar

- **Sınırlı araç çağırması.** Moshi bir diyaloji modelidir, bir ajan çerçevesi değil. Araçlar için hattın birleştirin.
- **Belirli ses koşullandırması.** Moshi tek bir eğitilmiş persona kullanır; klonlama ayrı bir eğitim çalışmasıdır.
- **Dil kapsamı.** Fransızca + İngilizce mükemmeldir; diğerleri sınırlı. Hibiki-Zero yardımcı olur ama yine de eğitim verisine ihtiyacınız vardır.
- **Kaynak maliyeti.** Tam bir Moshi oturumu bir GPU slotu tutar; ucuz bir kiracı- paylaşımlı (shared-tenant) dağıtım modeli değildir.

## Gönder

`outputs/skill-duplex-pipeline.md` olarak kaydedin. Bir ses ajanı iş yükü için hattı vs tam çift taraflı mimariyi, nedeniyle seçin.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. İki akışlı + iç monolog mimarisini sembolik olarak simüle eder.
2. **Orta.** Moshi'yi HuggingFace'den çekin, sunucuyu çalıştırın, bir diyaloğu test edin. Kullanıcı konuşmasının bitiminden Moshi yanıtının başlangıcına kadar duvar saati gecikmesini ölçün.
3. **Zor.** Ders 12 hatt ajanınızı alın ve 20 eşleştirilmiş test ifadesi üzerinde Moshi ile P50 gecikmesini karşılaştırın. Hattın mimari olarak nerede kazandığını yazın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|---------------------|------------------------|
| Tam çift taraflı | Aynı anda dinle ve konuş | Aynı modelde iki ses akışı aynı anda aktif. |
| İç monolog | Modelin metin akışı | Moshi ses çıktısıyla birlikte metin token'ları çıkarır. |
| Derinlik transformer'ı | Kod kitabı arası tahminci | 80 ms'lik tek bir kare içinde 8 kod kitabını tahmin eden küçük transformer. |
| Mimi | Kyutai'nin codec'i | 12.5 Hz × 8 kod kitabı; anlamsal+akustik; Moshi'yi besler. |
| Akışlı S2S | Ses → ses canlı | Parça parça çeviri/diyaloji, hata aşaması yok. |
| Arka kanal | "Hmm" tepkileri | Moshi turunu bozmadan küçük onaylamalar çıkarabilir. |

## İleri Okuma

- [Défossez et al. (2024). Moshi — konuşma-metin temel modeli](https://arxiv.org/html/2410.00037v2) — makale.
- [Kyutai Labs (2026). Hibiki-Zero](https://arxiv.org/abs/2602.12345) — hizalanmış veri olmadan akışlı çeviri.
- [Sesame (2025). Sırrın Vadisi'nin Ötesinde Ses](https://www.sesame.com/research/crossing_the_uncanny_valley_of_voice) — CSM teknik şartnamesi.
- [Kyutai — Moshi deposu](https://github.com/kyutai-labs/moshi) — kurulum + sunucu.
- [OpenAI — Realtime API](https://platform.openai.com/docs/guides/realtime) — kapalı ticari eş.
- [Kyutai — Gecikmeli Akış Modelleme](https://github.com/kyutai-labs/delayed-streams-modeling) — arka plandaki STT/TTS çerçevesi.
