---
name: voice-agent
description: 800ms altında ilk-ses-çıkışı, araya-girme (barge-in) yönetimi ve konuşma-ortası araç kullanımı ile gerçek-zamanlı bir ses ajanı inşa et
version: 1.0.0
phase: 19
lesson: 03
tags: [capstone, voice, webrtc, livekit, pipecat, asr, tts, streaming]
---

Bir alan (müşteri desteği, zamanlama, perakende asistanı) verildiğinde, barge-in, araç çağrıları ve paket kaybını ele alırken uçtan uca ilk-ses-çıkışını 800ms altında tutan bir WebRTC ses ajanı dağıt.

İnşa planı:

1. Mikrofon sesini akışlayan bir web istemcisiyle bir LiveKit Agents 1.0 odası kur. Telefon kapsamı için bir Twilio PSTN ağ geçidi ekle.
2. Akışlı ASR (barındırılan Deepgram Nova-3 veya bir g5.xlarge üzerinde faster-whisper Whisper-v3-turbo) çalıştır. Kısmi ve son transkriptlere abone ol.
3. 20ms çerçevelerinde Silero VAD v5 çalıştır. Konuşma-sonunda, en son kısmi transkripti LiveKit dönüş-dedektörüyle puanla; yalnızca VAD sessizliği >= 500ms ve tamamlama puanı >= 0,6 olduğunda tur-tamamlandı'ya bağlan.
4. LLM'i akışla (GPT-4o-realtime, Gemini 2.5 Flash Live veya kaskatlı Claude Haiku 4.5). İlk tokeni 200ms içinde TTS'e geçir.
5. TTS'i akışla (Cartesia Sonic-2 veya ElevenLabs Flash v3). İlk ses parçası, ilk LLM tokeninden 200ms içinde sunucudan ayrılmalıdır.
6. Araya-girme: SPEAKING veya THINKING sırasında VAD yeni kullanıcı konuşması tespit ettiğinde, TTS'i iptal et, kalan LLM çıktısını bırak, ASR'yi yeniden kur. Bir `tts_canceled` span'i yayınla.
7. Araç yan kanalı: fonksiyon çağrılarını eşzamanlı çalıştır; gecikme > 300ms ise, ses akışının asla durmaması için bir onay dolgusu yay.
8. 100 çağrı kaydet. Elenmiş transkriptlere karşı WER, Hamming VAD kıyaslaması üzerinde yanlış-kesim oranı, ilk-ses-çıkışı p50, NISQA MOS ve %3 paket düşüşü altında davranış ölç.
9. Tek bir g5.xlarge üzerinde sentetik bir arayanla 50 eşzamanlı çağrıya yük-testi uygula; sürdürülen ilk-ses-çıkışı p95'i raporla.

Değerlendirme rubriği:

| Ağırlık | Kriter | Ölçüm |
|:-:|---|---|
| 25 | Uçtan uca gecikme | 100 kaydedilmiş çağrıda p50 ilk-ses-çıkışı 800ms altında |
| 20 | Tur-alma kalitesi | Hamming VAD kıyaslaması üzerinde yanlış-kesim oranı %3 altında |
| 20 | Araç-kullanım doğruluğu | Konuşma ortası araç çağrıları sesi durdurmadan doğru veri döner |
| 20 | Paket kaybı altında güvenilirlik | %3 paket düşüşü enjekte edilmiş WER ve tur-alma kararlılığı |
| 15 | Değerlendirme iskeleti tamlığı | Genel yapılandırmayla yeniden üretilebilir ölçümler |

Kesin redler:

- Akışsız hatlar (toplu ASR, toplu TTS) gecikme hedefine ulaşamaz.
- TTS arabelleğini hemen iptal etmeyen herhangi bir araya-girme politikası. Gecikmeli iptal en kötü kullanıcı deneyimi regresyonlarını üretir.
- LLM akışını eşzamanlı olarak engelleyen araç çağrıları. Bir yan kanalda çalışmalıdırlar.

Ret kuralları:

- VAD veya dönüş-dedektörü olmadan dağıtmayı reddet. Sabit-zaman aşımı tur-alma kabul edilemez kesim oranları üretir.
- İnsan puanlı mı yoksa NISQA-vekaletli mi olduğunu belgelemeden MOS raporlama.
- En az 100 kaydedilmiş çağrı ve çağrı izlerini yayınlamadan "p50 gecikme X altında" raporlama.

Çıktı: LiveKit ajan işçisini, PSTN ağ geçidi yapılandırmasını, 100 çağrılık değerlendirme iskeletini, genel bir Langfuse ses panosunu, bir barındırılan rakiplerle (Retell, Vapi veya doğrudan OpenAI Realtime API) yan yana karşılaştırmayı ve gözlemlediğiniz en büyük üç tur-alma başarısızlığını ve her birini düzelten dedektör ayarlamasını açıklayan bir yazıyı içeren bir depo.
