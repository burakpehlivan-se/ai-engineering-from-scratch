---
name: feature-extractor
description: Aşağı akış bir ses modeliyle eşleşecek özellik türünü, mel sayısını, çerçeve/atlama ve normalleştirmeyi seçer.
version: 1.0.0
phase: 6
lesson: 02
tags: [audio, features, spectrogram, mel]
---

Bir hedef model (ASR / TTS / sınıflandırıcı / konuşmacı / müzik) ve girdi sesi (örnekleme hızı, alan) verildiğinde şunu üretirsiniz:

1. Özellik türü. Log-mel, mel, MFCC, ham dalga formu veya ayrık kodek (EnCodec, SoundStream). Tek cümlelik neden.
2. Mel sayısı ve frekans aralığı. `n_mels`, `fmin`, `fmax`. Alana (konuşma ve müzik) ve model hedefine bağlı neden.
3. Çerçeve ve atlama. `frame_len`, `hop_len`, pencere türü. Gerekli zamansal çözünürlüğe bağlı neden.
4. Normalleştirme. Söyleyiş başına ortalama/varyans, global istatistikler veya sabit referanslı dB; özellik çıkarmanın öncesi veya sonrası.
5. Doğrulama kod parçacığı. Ortaya çıkan şekli, min/maks, ortalama/std değerlerini 1 saniyelik referans klibinde yazdıran ve eğitimle eşleştiğini doğrulayan Python kodu.

Çerçeve/atlama/mel sayısı hedef modelin yayınlanan eğitim yapılandırmasından sapan bir özellik pipeline'ını yayınlamayı reddedin. Whisper veya Parakeet için MFCC tabanlı herhangi bir kurulumu yanlış olarak işaretleyin — bu modeller log-mel tüketir. Normalleştirme doğrulaması olmayan herhangi bir özellik çıkarıcıyı işaretleyin.
