---
name: video-brief
description: Bir video briefini 2026 video jeneratörü için model + istem + çekim planına çevir
version: 1.0.0
phase: 8
lesson: 10
tags: [video, difüzyon, sora, veo, kling]
---

Bir video briefi (süre, en-boy oranı, stil, özne, kamera planı, ses ihtiyaçları, sadakat çıtası, bütçe) verildiğinde, aşağıdakileri üret:

1. Model + barındırma. Sora, Veo 3, Kling 2.1, Runway Gen-3, Pika 2.0, CogVideoX, HunyuanVideo, WAN 2.2 veya Mochi-1. Süre / kalite / lisansa bağlı tek cümlelik gerekçe.
2. İstem iskelesi. (a) kamera dili (kuruluş, izleme, dolly, vinç, elde), (b) özne + eylem, (c) ışık + stil, (d) negatif istem veya stil geçişleri. Sora için 50-150, Runway için 20-60 token hedefle.
3. Çekim planı. Tek-klip vs birleştirilmiş çok-çekim, anahtar kare veya ilk kare çapaları, çekim başına I2V vs T2V.
4. Tohum + tekrarlanabilirlik. Çekim başına tohum, sürüm pin, araç repo'su.
5. QA kontrol listesi. Flicker, kimlik tutarlılığı, fizik ihlalleri, filigran uyumluluğu için kare kare kontrol.
6. Ses. Veo 3'te yerel, aksi takdirde tak-üzerine (ElevenLabs, Suno veya lisanslı kökler + dudak senkron geçişi).

Ücretsiz katmanda 1080p'de >10 sn sürekli hareket vaat etme (Pika / Kling / Runway 10 sn'de sınırlanır; daha uzun çalıştırmalar birleştirilir). Bırakma (release) olmadan gerçek insanların benzerliklerini üretme. 2026'da gerçek-zamanlı 4K üretim ima eden herhangi bir briefi işaretle - mevcut en iyi, barındırılan uç noktada 1080p'de 6 sn klip başına ~30 sn üretimdir.
