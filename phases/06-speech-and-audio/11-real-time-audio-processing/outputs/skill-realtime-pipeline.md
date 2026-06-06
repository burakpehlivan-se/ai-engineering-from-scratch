---
name: realtime-voice-pipeline
description: Hedef uçtan uca gecikme için taşıma, VAD, akan STT, LLM, akan TTS ve orkestrasyon seçer.
version: 1.0.0
phase: 6
lesson: 11
tags: [voice-agent, livekit, pipecat, silero, streaming, latency]
---

Hedef (gecikme P50/P95, dil, kanal, çevrimdışı vs bulut, çağrı hacmi) verildiğinde şunu üretirsiniz:

1. Taşıma. WebRTC (LiveKit / Daily) · WebSocket · SIP trunking (Twilio / Telnyx). Nedeni titreşim toleransı + kullanım senaryosu.
2. VAD + sıra devri. Silero VAD (açık, %99,5 TPR) · Cobra (ticari) · LiveKit turn-detector. Eşik, min konuşma süresi, sessizlik artığı.
3. Akan STT. Parakeet TDT (en hızlı açık) · Kyutai STT (flush trick ile) · Deepgram Nova-3 (API, ~150 ms) · Whisper-streaming. Neden.
4. LLM + streaming. TTS devreye girmeden önce ilk 20 token'ı sabitleyin. Model + streaming yapılandırması + istem enjeksiyonu için koruma setleri.
5. Akan TTS. Kokoro-82M (~100 ms TTFA) · Orpheus · Cartesia Sonic · ElevenLabs Turbo. Ses paketi veya klonlama koruması (Ders 8).
6. Orkestrasyon. LiveKit Agents · Pipecat · Vapi · Retell · özel Rust. Nedeni ekip becerileri + ölçek.
7. Gözlemlenebilirlik. Aşama başına P50/P95/P99 histogramları; yanlış-pozitif kesinti oranı; düşen çağrı oranı; çağrı örneklerinde WER.

Tüm söyleyişleri STT'den önce arabelleğe alan dağıtımları reddedin. Akış yapmayan TTS'yi reddedin. Ortalama gecikme ile değerlendirmeyi reddedin — P95 zorunlu kılın. >100k dakika/ay için yönetilen platformları (Vapi / Retell) kendin-yap-karşılaştırması olmadan reddedin.

Örnek girdi: "Otomobil sigortası teklifleri için ses ajanı. < 500 ms P95. İngilizce, ABD. Haftada 50k dakika. Uyumluluk: HIPAA'ya komşu (günlüklerde PII yok)."

Örnek çıktı:
- Taşıma: LiveKit Agents + Twilio SIP. Çağrı merkezi ölçeğinde kanıtlanmış, HIPAA modu isteğe bağlı.
- VAD: Silero VAD @ eşik 0,45, min konuşma 220 ms, sessizlik artığı 400 ms. LiveKit turn-detector katmanı.
- STT: Deepgram Nova-3 İngilizce (~150 ms P95); şirket içi denetim gerekirse Parakeet-TDT'ye geri dönüş.
- LLM: OpenAI realtime API ile GPT-4o streaming; bir son-okuyucu ile istem enjeksiyonuna karşı koruma; ilk 20 token'ı TTS'ye sabitleyin.
- TTS: Cartesia Sonic 2 (~150 ms TTFA, ses klonlama kullanılmıyor — önceden tanımlı ses).
- Orkestrasyon: LiveKit Agents. Üretim gözlemlenebilirliği Hamming AI ile.
- Günlükler: kalıcı hale getirmeden önce CVV / SSN / DOB'yi regex + NER geçişiyle ayıklayın. 30 gün saklayın.
