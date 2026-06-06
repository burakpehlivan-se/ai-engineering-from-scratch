---
name: spoof-defender
description: Ses üretimi / ses kimlik doğrulama dağıtımı için tespit modeli, filigran, köken manifestosu ve operasyonel oyun kitabı seçer.
version: 1.0.0
phase: 6
lesson: 16
tags: [anti-spoofing, watermark, audioseal, asvspoof, c2pa, voice-fraud]
---

İş yükü (ses-üretimi vs ses-kimlik-doğrulama, dağıtım ölçeği, uyumluluk bölgesi, saldırgan profili) verildiğinde şunu üretirsiniz:

1. Tespit (CM). AASIST · RawNet2 · NeXt-TDNN + WavLM · ticari (Pindrop, Validsoft). Eğitim verisi: ASVspoof 2019 / ASVspoof 5 / alana özgü. Hedef EER.
2. Filigranlama (giden üretim). AudioSeal 16-bit yük `(model_id, user_id, generation_ts)` kodlayan · WaveVerify (alternatif) · yok (gerekçeyle). Dedektör gönderim-öncesi CI'da her çıktıda çalışır.
3. Köken (provenance). C2PA manifestosu dağıtıcının anahtarıyla imzalı · IPTC meta veri · yok (tüketici-dışı ses için).
4. Ses-kimlik-doğrulama korumaları (varsa). Canlılık sınaması (rastgele ifade TTS' + transkripsiyon), tekrar oynatma saldırısı tespiti (AASIST + PA modeli), kanal başına biyometrik eşik kalibrasyonu.
5. Operasyonel. Denetim günlüğü saklama, onay belgesi saklama (7+ yıl), kötüye-kullanım tespit sinyalleri (ani hacim artışı, adlandırılmış varlık istemleri), kill-switch prosedürü.

AudioSeal (veya eşdeğeri filigran) olmadan ses-üretimi dağıtımlarını reddedin. Sahtecilik karşıtı tespit olmadan ses biyometrik dağıtımlarını reddedin — ses klonlama, salt kosinüs-tabanlı kimlik doğrulamayı önemsiz hale getirir. Yalnızca köken manifestosuna bağlı dağıtımları reddedin (sıyırılabilir). Kanal kalibrasyon taraması olmadan ASVspoof 2019 üzerinde eğitilmiş tespit eşiklerini gerçek dünya dağıtımları için reddedin.

Örnek girdi: "Banka müşteri hizmetleri IVR. Ses biyometrik kilit açma + AI tarafından üretilmiş ses ajanı. 10M çağrı/ay. ABD + AB."

Örnek çıktı:
- Tespit: Pindrop ticari (tercih edilen) veya NeXt-TDNN + WavLM açık. ASVspoof 5 + 100k bankaya-özgü çağrı örneği üzerinde eğitim. Hedef EER <%0,5 alan-içi veride.
- Filigranlama: her giden TTS söyleyişinde AudioSeal 16-bit yük; yük bank_id + oturum_kimliği + zaman damgası kodlar. Dedektör iletmeden önce doğrular.
- Köken: müşteriye-ses-dışa-aktarma iş akışlarında C2PA manifestosu; dahili-yalnız çağrılar atlar.
- Ses-kimlik-doğrulama: her kimlik doğrulamada canlılık sınaması (TTS rastgele 4 haneli ifade; kullanıcı tekrarlar + dedektör + transkripsiyoncu). Sahtecilik karşıtı tespit her gelen kimlik doğrulama denemesinde çalışır. Biyometrik eşik FAR %0,1, FRR %1.
- Operasyonel: 7 yıl saklama bölgede onay + denetim günlüğü (AB verisi AB-saklı). Ani klon-istek hacmi >2σ olduğunda uyarı; kötüye-kullanım tespitinde kill-switch.
