---
name: voice-pipeline
description: Barge-in, confidence gating ve latency budget enforcement ile Pipecat şekilli bir voice pipeline (VAD + STT + LLM + TTS + transport) iskele.
version: 1.0.0
phase: 14
lesson: 22
tags: [voice, pipecat, livekit, webrtc, latency]
---

Bir voice ürün spesifikasyonu (dil, transport, sağlayıcılar) verildiğinde, frame-tabanlı bir pipeline iskele.

Şunları üret:

1. `kind`, `payload`, `direction` (downstream / upstream) ile `Frame` tipi.
2. Processor'lar: `VAD`, `STT`, `LLM`, `TTS`, `Transport`. Her biri `process(frame)` ile.
3. Processor'ları ileri ve geri zincirleyen `link()` helper'ı.
4. Cancel frame işleme: transport'tan TTS'ye, LLM'ye, STT'ye UPSTREAM yol, her aşamada bekleyen işi düşürür.
5. Observer'lar: aşama başına latency metrikleri; bir processor'ı geçen her frame için bir OTel span'ı yayar (Ders 23).
6. STT üzerinde confidence gate: eşiğin altında, transcript yerine "lütfen tekrar eder misiniz" text frame'i yayar.

Sert reject sebepleri:

- UPSTREAM işleme olmadan pipeline. Barge-in voice için opsiyonel değildir.
- Streaming olmadan LLM çağrıları. First-token latency baskındır; streamed olmalıdır.
- Confidence-blind STT. Yanlış transcript'leri LLM'e beslemek yanlış yanıtlar üretir.

Refusal kuralları:

- End-to-end latency soğuk bir çalıştırmada 1500ms'yi aşarsa, gönderimi reddet. Zinciri optimize et veya bir MultimodalAgent (LiveKit direct-audio) kullan.
- Ürün telephony-first ise ve pipeline'da SIP adapter yoksa, reddet. LiveKit SIP veya bir platform (Vapi/Retell) üzerinden yönlendir.
- Ürün, transit sırasında şifreleme olmadan PII sesi taşıyorsa, reddet.

Çıktı: `frames.py`, `processors.py`, `pipeline.py`, `observers.py`, latency budget'ını, barge-in tasarımını ve transport seçimini açıklayan `README.md`. Ders 23'e (OTel), Ders 24'e (observability backends) veya WebRTC specifics için LiveKit docs'a işaret eden bir "sırada ne okumalı" ile bitir.
