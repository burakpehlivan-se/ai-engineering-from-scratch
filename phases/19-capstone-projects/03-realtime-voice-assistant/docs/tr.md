# Capstone 03 — Gerçek Zamanlı Sesli Asistan (ASR'den LLM'ye TTS'ye)

> Doğru hissettiren bir sesli ajanın uçtan uca gecikmesi 800ms'nin altındadır, ne zaman konuşmayı bıraktığınızı bilir, araya girmeyi (barge-in) yönetir ve takılmadan bir tool çağırabilir. Retell, Vapi, LiveKit Agents ve Pipecat hepsi 2026'da bu çıtayı geçti. Bunu aynı şekille yapıyorlar: akış (streaming) ASR, bir dönüş-algılayıcısı (turn-detector), akış LLM ve akış TTS — hepsi her sıçramada agresif gecikme bütçeleriyle WebRTC üzerinden bağlanmış. Bir tane inşa edin, WER, MOS ve yanlış-kesme oranını ölçün ve paket kaybı altında çalıştırın.

**Type:** Capstone
**Languages:** Python (agent + pipeline), TypeScript (web client)
**Prerequisites:** Phase 6 (speech and audio), Phase 7 (transformers), Phase 11 (LLM engineering), Phase 13 (tools), Phase 14 (agents), Phase 17 (infrastructure)
**Phases exercised:** P6 · P7 · P11 · P13 · P14 · P17
**Time:** 30 saat

## Problem

Ses, 2025-2026'nın en hızlı hareket eden yapay zekâ UX kategorisi oldu. Teknik tavan her çeyrekte düştü. OpenAI Realtime API, Gemini 2.5 Live, Cartesia Sonic-2, ElevenLabs Flash v3, LiveKit Agents 1.0 ve Pipecat 0.0.70 hepsi 800ms altı ilk-ses-dışarı'yı erişilebilir kıldı. Çıta yalnızca gecikme değil. Etkileşim hissi: kullanıcının sözünü kesmemek, kendiniz kesilmemek, cümle ortası kesintiden kurtulmak, ses akışını durdurmadan konuşma ortasında bir tool çağırmak, sarsıntılı mobil ağlarda hayatta kalmak.

Üç REST çağrısını birbirine dikerek oraya varamazsınız. Mimari uçtan uca akış boru hattıdır. İnşa edin ve hata modları görünür olur: arka plandaki TV'de tetiklenen telefon sesi için ayarlanmış bir VAD, hiç gelmeyen noktalamayı bekleyen bir dönüş-algılayıcısı, yayınlamadan önce 400ms arabellekleyen bir TTS. Capstone, bunları yük altında birer birer düzeltmek ve bir gecikme-ve-kalite raporu yayınlamaktır.

## Concept

Boru hattının beş akış aşaması var: **ses girişi** (tarayıcı veya PSTN'den WebRTC), **ASR** (Deepgram Nova-3 veya faster-whisper'dan akış kısmi transkriptler), **dönüş algılama** (VAD artı kısmi transkriptleri tamamlama ipuçları için okuyan küçük bir dönüş-algılayıcı modeli), **LLM** (dönüş tamamlandı diye yargılanır yargılanmaz tokenları akıtmak), **TTS** (ilk LLM tokenından ~200ms içinde akış sesi dışarı).

Üç yatay kesim konusu. **Araya girme (barge-in)**: ajan konuşurken kullanıcı konuşmaya başladığında, TTS iptal olur ve ASR hemen devralır. **Tool kullanımı**: konuşma ortası fonksiyon çağrıları (hava durumu, takvim) sesi duraksatmadan yan bir kanalda çalışmalıdır; ajan, gecikme 300ms'yi aşarsa bir onay token'ı ("bir saniye...") öceden doldurur. **Geri basınç (backpressure)**: paket kaybı altında, kısmi transkriptler tutulur, VAD konuşma-kapısı eşiğini yükseltir ve ajan onaylanmamış bir mesajın üzerine konuşmaktan kaçınır.

Ölçüm çıtası niceldir. Hamming VAD kıyaslamasında 15 dB SNR'de WER %8'in altında. 100 ölçülmüş çağrıda ilk-ses-dışarı p50 800ms'nin altında. Yanlış-kesme oranı %3'ün altında. TTS MOS 4.2'nin üstünde. Tek bir g5.xlarge üzerinde 50 eşzamanlı çağrı. Bu sayılar teslim edilen şey.

## Architecture

```
browser / Twilio PSTN
        |
        v
   WebRTC / SIP edge
        |
        v
  LiveKit Agents 1.0  (or Pipecat 0.0.70)
        |
   +----+--------------+--------------+-----------------+
   |                   |              |                 |
   v                   v              v                 v
  ASR              VAD v5         turn-detector     side-channel
(Deepgram         (Silero)          (LiveKit)        tools
 Nova-3 /         speech-gate    completion score    (weather,
 Whisper-v3)      per 20ms        on partials        calendar)
   |                   |              |
   +--------+----------+--------------+
            v
        LLM (streaming)
     GPT-4o-realtime / Gemini 2.5 Flash /
     cascaded Claude Haiku 4.5
            |
            v
        TTS streaming
     Cartesia Sonic-2 / ElevenLabs Flash v3
            |
            v
     audio back to caller
            |
            v
   OpenTelemetry voice traces -> Langfuse
```

#### Açıklama

Bu akış şeması bir sesli ajanın beş paralel aşamasını gösterir. Tarayıcı veya Twilio PSTN'den gelen ses WebRTC üzerinden LiveKit Agents 1.0'a girer. Burada dört aşama paralel çalışır: Deepgram Nova-3 veya Whisper-v3 akış kısmi transkriptler üretir, Silero VAD v5 ses çerçevelerini sınıflandırır, LiveKit dönüş-algılayıcısı kısmi transkriptlerdeki tamamlama skorunu değerlendirir ve hava durumu/takvim gibi tool'lar yan kanalda çalışır. Dönüş tamamlandığında LLM token akıtmaya başlar, ilk token TTS'e geçer ve Cartesia Sonic-2 veya ElevenLabs Flash v3 akış sesi üretir. Tüm süreç OpenTelemetry voice span'leri ile Langfuse'a gider.

## Stack

- Taşıma: LiveKit Agents 1.0 (WebRTC) artı Twilio PSTN ağ geçidi; alternatif çatı olarak Pipecat 0.0.70
- ASR: Deepgram Nova-3 (akış, 300ms altı ilk kısmi) veya faster-whisper Whisper-v3-turbo self-hosted
- VAD: Silero VAD v5 artı LiveKit dönüş-algılayıcısı (kısmi transkriptleri okuyan küçük transformer)
- LLM: OpenAI GPT-4o-realtime sıkı entegrasyon için, Gemini 2.5 Flash Live veya kaskadlanmış Claude Haiku 4.5 (akış tamamlamalar, ayrı ses yolu)
- TTS: Cartesia Sonic-2 (en düşük ilk-byte), ElevenLabs Flash v3 veya self-host için açık kaynak Orpheus
- Tool'lar: Hava durumu/takvim/rezervasyon için FastMCP yan kanalı; tool 300ms'den uzun sürerse ajan doldurucu (filler) ön-yayar
- Gözlemlenebilirlik: OpenTelemetry voice span'leri, sesli kayıttan tekrar oynatmalı Langfuse sesli izler
- Dağıtım: Self-hosted Whisper + Orpheus için tek bir g5.xlarge (24GB VRAM); en düşük gecikme için hosted API'ler

## Build It

1. **WebRTC oturumu.** Bir LiveKit odası ve mikrofon sesini akıtan bir web istemcisi kurun. Sunucuda, odaya katılan bir ajan işçisi ekleyin.

2. **ASR akışı.** 20ms PCM çerçevelerini Deepgram Nova-3'e (veya GPU'da faster-whisper'a) besleyin. Kısmi ve son transkriptlere abone olun. Kısmi başına gecikmeyi günlüğe kaydedin.

3. **VAD ve dönüş algılayıcısı.** Çerçeve akışında Silero VAD v5'i çalıştırın. Konuşma-sonu olayında, en son kısmi transkript üzerinde LiveKit dönüş-algılayıcısını tetikleyin. Yalnızca VAD 500ms sessizlik bildirdiğinde ve dönüş-algılayıcısı tamamlama > 0.6 puanladığında "dönüş tamamlandı" olarak işleyin.

4. **LLM akışı.** Dönüş tamamlandığında, devam eden konuşma artı son transkriptle LLM çağrısını başlatın. Tokenları dışarı akıtın. İlk token'da TTS'e devredin.

5. **TTS akışı.** Cartesia Sonic-2 ses parçalarını geri akıtır. İlk parça, ilk LLM tokenından 200ms içinde sunucudan ayrılmalıdır. Parçaları LiveKit odasına yayınlayın; istemci WebRTC jitter arabelleği üzerinden oynatır.

6. **Araya girme (barge-in).** TTS oynatırken VAD yeni kullanıcı konuşması algılarsa, TTS akışını hemen iptal edin, kalan LLM çıktısını bırakın ve ASR'yi yeniden kurun. Bir `tts_canceled` span'i yayınlayın.

7. **Tool yan kanalı.** Hava durumu ve takvimi fonksiyon çağrısı tool'ları olarak kaydedin. Çağrıldıklarında, eşzamanlı olarak tetikleyin; 300ms içinde çözülmezse, LLM'in "bir saniye, kontrol edeyim" demesini sağlayın; tool döndüğünde devam edin.

8. **Eval çatısı.** 100 çağrı kaydedin. WER (holdout transkriptine karşı), yanlış-kesme oranı (kullanıcı cümle ortasındayken TTS iptal edildi), ilk-ses-dışarı p50, TTS MOS (insan veya NISQA) ve bir jitter-kaybı testi (paketlerin %3'ünü bırakın) hesaplayın.

9. **Yük testi.** Tek bir g5.xlarge'da sentetik bir arayan ile 50 eşzamanlı çağrıyı çalıştırın. Sürdürülebilir ilk-ses-dışarı p95'i ölçün.

## Use It

```
caller: "what is the weather in tokyo tomorrow"
[asr  ] partial @280ms: "what is the"
[asr  ] partial @540ms: "what is the weather"
[turn ] completion score 0.82 at @820ms; commit
[llm  ] first token @960ms
[tool ] weather.tokyo tomorrow -> 68/52 partly cloudy @1140ms
[tts  ] first audio-out @1040ms: "Tokyo tomorrow will be partly cloudy..."
turn latency: 1040ms user-stop -> audio-out
```

#### Açıklama

Bu zaman çizelgesi tek bir sesli dönüşün tam gecikme bütçesini gösterir. Kullanıcı "what is the weather in tokyo tomorrow" der. İlk kısmi transkript 280ms'de, ikincisi 540ms'de gelir. Dönüş-algılayıcısı 820ms'de tamamlama skoru 0.82 ile dönüşü tamamlar. LLM 960ms'de ilk tokenı verir. Yan kanaldaki hava durumu tool'u 1140ms'de yanıtlar. TTS'in ilk ses çıktısı 1040ms'de olur — yani 1040ms'lik uçtan uca gecikme hedefi 800ms'yi hafifçe aşar; bu, gerçek dünyada ayarlama gerektiren bir noktadır.

## Ship It

`outputs/skill-voice-agent.md` teslim edilen şeydir. Bir alan (müşteri desteği, zamanlama veya kiosk) verildiğinde, ölçüm çıtasına ayarlanmış bir LiveKit ajanını ASR/VAD/LLM/TTS boru hattıyla kurar. Değerlendirme ölçütü:

| Ağırlık | Ölçüt | Nasıl ölçülür |
|:-:|---|---|
| 25 | Uçtan uca gecikme | 100 kaydedilmiş çağrıda p50 ilk-ses-dışarı 800ms altında |
| 20 | Dönüş-alma kalitesi | Hamming VAD kıyaslamasında yanlış-kesme oranı %3 altında |
| 20 | Tool-kullanım doğruluğu | Sesi duraksatmadan doğru veri döndüren konuşma-ortası tool çağrıları |
| 20 | Paket kaybı altında güvenilirlik | Enjekte edilen %3 paket bırakma ile WER ve dönüş-alma kararlılığı |
| 15 | Eval çatısı tamlığı | Herkese açık konfigürasyonla tekrarlanabilir ölçümler |
| **100** | | |

## Exercises

1. Deepgram Nova-3'ü bir g5.xlarge üzerinde faster-whisper v3 turbo ile değiştirin. Gecikme ve WER farkını ölçün. CPU-vs-GPU kararlarının nerede önemli olduğunu belirleyin.

2. Bir araya girme-arbitraj politikası ekleyin: tool çağrısı sırasında kullanıcı araya girdiğinde ajan ne yapar? Üç politikayı karşılaştırın (sert iptal, tool'u bitir-sonra-dur, sonraki dönüşü kuyruğa al).

3. Düşmanca bir dönüş-algılayıcı testi çalıştırın: kullanıcıya cümle ortasında uzun duraklamalar verin. En düşük yanlış-kesme için VAD sessizlik eşiğini ve dönüş-algılayıcısı skor eşiğini 900ms'yi aşmadan ayarlayın.

4. Aynı ajanı Twilio üzerinden PSTN'de dağıtın. PSTN ilk-ses-dışarı'yı WebRTC ile karşılaştırın. Jitter arabelleği ve kodek farklılıklarını açıklayın.

5. İngilizce olmayan diller (Japonca, İspanyolca) için ses etkinliği algılama ekleyin. Silero VAD v5 yanlış tetikleme oranını dile-özgü ince-ayarlara karşı ölçün.

## Key Terms

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|------|----------------------|----------------------------|
| Dönüş algılama | "Söz sonu" | VAD sessizliği ve kısmi bir transkript verildiğinde kullanıcının konuşmayı bitirdiğine karar veren sınıflandırıcı |
| Araya girme (barge-in) | "Kesme işleme" | VAD yeni kullanıcı konuşması algıladığında TTS'i oynatma ortasında iptal etmek |
| İlk-ses-dışarı | "Gecikme" | Kullanıcının konuşmayı bırakmasından ilk ses paketinin sunucudan ayrılmasına kadar geçen süre |
| VAD | "Konuşma kapısı" | Ses çerçevelerini konuşma vs sessizlik olarak sınıflandıran model; Silero VAD v5 2026 varsayılanıdır |
| Jitter arabelleği | "Ses yumuşatma" | Ağ değişkenliğini emmek için paketleri kısa süre tutan istemci tarafı arabellek |
| Doldurucu (filler) | "Onay token'ı" | Tool yavaşken sessizlikten kaçınmak için ajanın yayınladığı kısa ifade |
| MOS | "Ortalama görüş puanı" | Algısal ses kalitesi derecesi; NISQA otomatik vekildir |

## Further Reading

- [LiveKit Agents 1.0](https://github.com/livekit/agents) — referans WebRTC ajan çatısı
- [Pipecat](https://github.com/pipecat-ai/pipecat) — alternatif Python-öncelikli akış ajan çatısı
- [OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime) — tümleşik ses modelleri için referans
- [Deepgram Nova-3 documentation](https://developers.deepgram.com/docs) — akış ASR referansı
- [Silero VAD v5](https://github.com/snakers4/silero-vad) — VAD referans modeli
- [Cartesia Sonic-2](https://docs.cartesia.ai) — düşük gecikmeli TTS referansı
- [Retell AI architecture](https://docs.retellai.com) — üretim sesli ajan mimarisi
- [Vapi.ai production stack](https://docs.vapi.ai) — alternatif üretim referansı
