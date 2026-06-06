---
name: asr-configurator
description: Yeni bir konuşma işleme hattı için ASR modeli (Whisper varyantı / Moonshine / faster-whisper) ve kod çözme parametreleri seç
version: 1.0.0
phase: 7
lesson: 10
tags: [transformers, whisper, asr, konuşma]
---

Bir konuşma görevi (transkripsiyon / çeviri / akış / cihaz-üstü), dil(ler), ses özellikleri (gürültü, aksan, süre) ve gecikme/kalite hedefleri verildiğinde, aşağıdakileri üret:

1. Model seçimi. Şunlardan biri: faster-whisper large-v3-turbo (üretim varsayılanı), whisper large-v3 (en yüksek kalite, çok dilli), whisper medium (orta seviye), Moonshine base (uç), distil-whisper (2× daha hızlı İngilizce). Tek cümlelik gerekçe.
2. Nicemleme. int8_float16 (CPU varsayılanı), float16 (GPU varsayılanı), fp32 (araştırma). VRAM etkisini işaretle.
3. Kod çözme. Işın genişliği (akış için tipik 5, 1), sıcaklık geri dönüş zamanlaması, log-olasılık eşiği, konuşma-yok eşiği, VAD geçidi açık/kapalı.
4. Parçalama. 30 sn sabit pencere veya akış parçaları (tipik olarak 2 sn örtüşmeyle 10 sn) + VAD tabanlı bölümleme. Örtüşmeler için sonradan birleştirme stratejisini belgele.
5. Son işleme. Zaman damgası hizalama (WhisperX zorunlu hizalama), noktalama restorasyonu, konuşmacı ayrımı (pyannote). Hangilerinin görev için gerekli olduğunu işaretle.

Üretim için düz OpenAI Whisper (referans uygulama) önerme — `faster-whisper` aynı çıktılarla 4× daha hızlı. Belgelenmiş neden olmadan VAD olmadan akış ASR gönderme. Girdi muhtemelen çok konuşmacılı olduğunda tek konuşmacı varsayımını işaretle.
