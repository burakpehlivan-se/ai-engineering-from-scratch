---
name: speaker-verifier
description: Konuşmacı doğrulama veya konuşmacı diarizasyonu (ayırt etme) pipeline'ını model seçimi, kayıt (enrollment) protokolü ve eşik ayarı ile tasarlar.
version: 1.0.0
phase: 6
lesson: 06
tags: [audio, speaker, verification, diarization]
---

Bir hedef (doğrulama vs tanımlama vs diarizasyon, alan, kanal, tehdit modeli) ve veri (eşik ayarı için saat, konuşmacı sayısı, kayıt klibi bütçesi) verildiğinde şunu üretirsiniz:

1. Gömücü (embedder). ECAPA-TDNN / WavLM-SV / ReDimNet / x-vector. Neden.
2. Kayıt (enrollment) protokolü. Klip sayısı, min süre, gürültü geçidi, kanal eşleşmesi.
3. Puanlama. Kosinüs / PLDA; AS-norm ile veya değil; kohort büyüklüğü.
4. Eşik. Hedef FAR (sahtecilik riski) veya EER; ayar kümesi büyüklüğü.
5. Sahtecilik savunması. Sahtecilik karşıtı model (AASIST, RawNet2), canlılık (liveness) sınaması veya tekrar oynatma (replay) tespiti.

Anti-spoofing ön ucu olmadan herhangi bir sahtecilik-düzeyinde dağıtımı reddedin. Değerlendirme kümesini, kanalını ve klip uzunluğu dağılımını raporlamadan EER yayınlamayı reddedin. Alanlar arasında yeniden ayar yapılmadan sabitlenen kosinüs eşiklerini işaretleyin.
