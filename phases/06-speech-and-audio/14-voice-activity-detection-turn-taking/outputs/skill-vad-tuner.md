---
name: vad-tuner
description: Bir ses ajanı için VAD (Ses Etkinliği Tespiti) modeli, eşik, sessizlik artığı, ön kayıt ve sıra tespiti stratejisi seçer.
version: 1.0.0
phase: 6
lesson: 14
tags: [vad, silero, cobra, turn-detection, flush-trick]
---

İş yükü (tüketici / çağrı merkezi / uç / erişilebilirlik; gürültü profili; dil karışımı; gecikme) verildiğinde şunu üretirsiniz:

1. VAD. Silero VAD (varsayılan) · Cobra (ticari doğruluk) · pyannote segmentasyonu (diarizasyon düzeyinde) · WebRTC VAD (eski / küçük). Tek cümlelik neden.
2. Parametreler. Eşik (0,3-0,5), min konuşma (200-300 ms), sessizlik artığı (400-800 ms), ön kayıt (250-500 ms).
3. Anlamsal sıra tespiti. Etkin (LiveKit turn-detector veya özel MLP) veya değil. Nedeni beklenen kullanıcı konuşma örüntülerine bağlı.
4. Flush trick. STT destekliyorsa etkin (Kyutai / Deepgram) veya değil. Beklenen gecikme tasarrufu.
5. Korumalar. Min süreden kısa konuşmayı reddedin; her zaman ön kaydı saklayın; kullanıcı başına sessizlik-artığı geçersiz kılmasını sınırlandırın; VAD hizmeti düşerse başarısız-aç (her şeyi konuşma olarak ele alın).

Üretim için yalnızca enerji-tabanlı VAD'yi reddedin — çok gürültülü. Sıfır sessizlik-artığını reddedin — kullanıcıları keser. Özel Silero mevcutken Whisper-tabanlı VAD'yi reddedin (daha yavaş, daha az doğru).

Örnek girdi: "Havayolu yeniden rezervasyon için çağrı merkezi IVR. Gürültülü arka plan (havalimanı). İngilizce + İspanyolca. < 500 ms sıra tespiti."

Örnek çıktı:
- VAD: Gürültü direnci avantajı için Cobra (ticari). Maliyet engelleyiciyse Silero'ya geri dönüş.
- Parametreler: eşik 0,4 (havalimanı gürültü tabanı yüksek); min konuşma 300 ms; sessizlik artığı 600 ms (kullanıcılar IVR'de uçuş numaralarını okumak için sık sık durur); ön kayıt 400 ms.
- Anlamsal sıra: LiveKit turn-detector etkin — cümle ortası duraklamalar yaygın ("Uçuşumu değiştirmem lazım... yarına").
- Flush trick: Deepgram streaming'de etkin. Beklenen tasarruf: 400 ms → 150 ms sıra sonu gecikmesi.
- Korumalar: Cobra/Deepgram ulaşılamazsa başarısız-aç; ayar için her VAD-tetiklenen olayı denetim günlüğüne kaydedin.
