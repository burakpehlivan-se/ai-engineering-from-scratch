---
name: audio-loader
description: Ham bir ses dosyasını hedef modelin beklentilerine göre doğrular ve güvenli şekilde yeniden örnekler.
version: 1.0.0
phase: 6
lesson: 01
tags: [audio, speech, preprocessing]
---

Bir ses dosyası (yol, kanal sayısı, örnekleme hızı, bit derinliği, kodek) ve bir hedef model (gerekli örnekleme hızı ve kanal sayısı olan ASR / TTS / sınıflandırıcı) verildiğinde şunu üretirsiniz:

1. Uyuşmazlıklar. Dosyanın hedefle eşleşmediği her boyutu listeleyin (sr, kanallar, süre tabanı, kırpma kontrolü).
2. Yeniden örnekleme planı. Kaynak sr, hedef sr, yeniden örnekleme kütüphanesi (`torchaudio.transforms. Resample` veya `librosa.resample`), anti-aliasing filtre türü.
3. Kanal planı. Mono katlama stratejisi (ortalama veya yalnızca sol) veya modelin desteklediği durumda çok kanallı geçiş.
4. Normalleştirme. Tepe veya RMS normalleştirme, dBFS hedefi, kırpma koruması.
5. Doğrulama kod parçacığı. Dosyayı yükleyen, dönüşümleri çalıştıran ve son dizinin `(target_sr, dtype, channel_count, range)` ile eşleştiğini doğrulayan Python kodu.

Anti-aliasing filtresi olmadan yeniden örneklemeyi reddedin. Yeniden yapılandırma filtresi olmadan 2x'in üzerinde yukarı örneklemeyi reddedin. Kırpma tepeleri ±0,999'un üzerinde veya DC ofseti ±0,01'in üzerinde olan herhangi bir girdi dosyasını işaretleyin.
