---
name: codec-picker
description: Belirli bir üretken veya sıkıştırma görevi için bir sinirsel ses kodeği (EnCodec / DAC / SNAC / Mimi) seçer.
version: 1.0.0
phase: 6
lesson: 13
tags: [codec, encodec, dac, snac, mimi, rvq, semantic-tokens]
---

Görev (üretken LM, sıkıştırma, tam çift yönlü diyalog, müzik düzenleme, sadakat hedefi) verildiğinde şunu üretirsiniz:

1. Kodek. EnCodec-24k · EnCodec-48k · DAC-44.1k · SNAC-24k · Mimi · (yedek: sinirsel-olmayan sıkıştırma için Opus). Tek cümlelik neden.
2. Kare hızı + codebook'lar. Bitrate bütçesi, codebook sayısı (genellikle 4-12), hedef klip süresi için dizi uzunluğu.
3. Tokenizasyon şeması. Düz vs hiyerarşik (SNAC) vs anlamsal+akustik (Mimi). LM'nin token'ları nasıl tükettiği.
4. Kod çözücü. Kodek-içi kod çözücü · harici vocoder (HiFi-GAN) · yalnızca LM (vocoder yok, kodek token'larını doğrudan tahmin et). Neden.
5. Eğitim çıkarımları. Kodlayıcı/kod çözücü eğitmek gerekiyor mu? Alana ince ayar (yalnızca konuşma → alana özgü müzik)? Dondurulmuş hazır mı?

DAR gecikme bütçelerinde AR-LM iş yükleri için DAC'ı reddedin — 86 Hz kare hızı × 8 codebook = 10 sn başına 5.504 token, hızlı üretim için çok uzun. Mimi'yi müzik için reddedin — konuşmaya ayarlı. Anlamsal-koşullu üretim için EnCodec'i reddedin — anlamsal codebook yok, metinden bulanık konuşma.

Örnek girdi: "Metinden-konuşmaya TTS için bir AR LM inşa edin. Hedef TTFA 200 ms. Yalnızca İngilizce."

Örnek çıktı:
- Kodek: Mimi. Anlamsal+akustik ayrım, metin → codebook 0 → codebooks 1-7 çarpanlarına ayırmayı sağlar; hem hızlıdır hem ses klonlamayı destekler.
- Kare hızı + codebook'lar: 12,5 Hz · 8 codebook · 4,4 kbps. 10 sn = 1.000 token.
- Tokenizasyon: önce codebook 0'ı metin + konuşmacı referansından tahmin edin; sonra codebook 1-7'yi codebook 0 + konuşmacı referansı verildiğinde tahmin edin (derinlik-transformer örüntüsü).
- Kod çözücü: Mimi'nin yerleşik kod çözücüsü, harici vocoder gerekmez.
- Eğitim: metin-kodek LM'sini eğitin; Mimi'yi dondurun.
