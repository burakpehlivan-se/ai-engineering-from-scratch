---
name: audio-brief
description: Bir ses briefini TTS, müzik ve SFX genelinde model + istem + değerlendirme planına çevir
version: 1.0.0
phase: 8
lesson: 11
tags: [ses, tts, müzik, sfx, codec]
---

Bir ses briefi (görev: TTS / müzik / SFX / ses klonlama, süre, stil, ses veya tür, lisans kısıtlamaları, gerçek-zamanlı veya çevrimdışı, kalite çıtası) verildiğinde, aşağıdakileri üret:

1. Model + barındırma. ElevenLabs V3, OpenAI TTS, XTTS v2, Suno v4, Udio, Stable Audio 2.5, MusicGen 3.3B, AudioCraft 2 veya GPT-4o realtime. Tek cümlelik gerekçe.
2. İstem biçimi. TTS: metin + ses istemi (3-10 sn örnek veya ses kimliği) + duygu / hız etiketleri. Müzik: tür + enstrümantasyon + ruh hali + BPM + yapısal işaretler. SFX: onomatopoeia + kaynak + süre ipucu.
3. Codec + jeneratör + vocoder zinciri. Belirli codec'i (Encodec 32 kHz, DAC 44 kHz, özel) ve jeneratör seçimini (token-AR vs akış-eşleme) adlandır.
4. Tohum + tekrarlanabilirlik. Tohum pin, sürüm pin, istem karması.
5. Değerlendirme. MOS (ortalama görüş puanı) veya TTS için A/B, müzik için CLAP skoru, TTS transkripsiyonu için CER, SFX için kullanıcı dinleme testi.
6. Korumalar. Ses klonlama onayı + filigran (PerTh / SynthID-audio), müzik çıktısında telif taraması, eğitim verisi politikası kontrolü.

Sahibinin doğrulanmış onayı olmadan herhangi bir sesi klonlama (Kaset dönemi "3 saniyelik istem" onay değildir). Lisanssız referans materyalle müzik gönderme. Akışlı token-AR model kullanmayan <200 ms gerçek-zamanlı hedefi işaretle - 2026'da difüzyon tabanlı ses 300 ms altı TTFB'yi karşılayamaz.
