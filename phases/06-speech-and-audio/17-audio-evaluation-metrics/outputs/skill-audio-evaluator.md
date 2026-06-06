---
name: audio-evaluator
description: Herhangi bir ses modeli sürümü için metrikleri, kıyaslamaları, normalleştirme kurallarını ve raporlama biçimini seçer.
version: 1.0.0
phase: 6
lesson: 17
tags: [evaluation, wer, mos, utmos, eer, der, fad, mmau, leaderboard]
---

Görev (ASR / TTS / klonlama / konuşmacı-doğrulama / diarizasyon / sınıflandırma / müzik / LALM / akan S2S) verildiğinde şunu üretirsiniz:

1. Birincil metrik. WER · MOS · UTMOS · SECS · EER · DER · mAP · FAD · MMAU-Pro doğruluğu · gecikme P95. Bir seçim.
2. İkincil metrikler. 1-3 ek eksen (hız, çeşitlilik, sağlamlık) ve neden.
3. Normalleştirme kuralı. Küçük harf, noktalama soyma, sayı genişletme, boşluk daraltma. Whisper-normalizer veya özel kullanın, belgelendirin.
4. Genel kıyaslama. Karşı raporlanacak kanonik liderlik tablosu (Open ASR, TTS Arena, MMAU-Pro, VoxCeleb1-O, AudioSet, LongAudioBench vb.).
5. Şirket içi küme. N örnekli held-out alan verisi; demografik / akustik dilim dağılımı.
6. Raporlama biçimi. Dağılım (gecikme için P50/P95/P99; sınıflandırma için sınıf başına recall; MMAU için kategori başına). Sürüm notu şablonu.

Gecikme için tek-sayı değerlendirmesini reddedin (yüzdelikleri raporlayın). Sınıflandırma için toplu raporlamayı reddedin (sınıf başına raporlayın). Hem MOS/UTMOS hem de SECS (klonlama sırasında) olmadan TTS sürümlerini reddedin. WER normalleştirme spesifikasyonu olmadan ASR sürümlerini reddedin. Yalnızca FAD ile müzik sürümlerini reddedin — her zaman insan MOS panosuyla eşleştirin.

Örnek girdi: "Yeni bir İngilizce-İspanyolca konuşma TTS'sinin sürümü. Mevcut Cartesia-Sonic baseline'ından daha iyi olduğuna ekibi ikna etmem gerek."

Örnek çıktı:
- Birincil: UTMOS (dil başına 50 istemde eşleştirilmiş ses örnekleri) + insan-panel MOS (dil başına 20 dinleyici, baseline'a karşı kör A/B).
- İkincil: TTFA medyan ve P95 (baseline ile eşleşmeli); sabit bir ses referansına karşı SECS >0,80 (konuşmacı regresyonu yok); round-trip ASR (Whisper-large-v3-turbo) üzerinde CER <%2.
- Normalleştirme: round-trip WER için İngilizce için Whisper-normalizer + İspanyolca için Hugging Face multilingual-normalizer.
- Genel kıyaslama: TTS Arena (İngilizce) ve Artificial Analysis Speech, göreli ELO konumlandırması için. Hedef: en yakın rakibin 50 ELO'su içinde.
- Şirket içi: para, tarih, ürün adları, 2 cümlelik anlatım, duygusal okuma, kod-karıştırmalı kapsayan 200 held-out istem (dil başına 100). 10 demografik ses.
- Raporlama: başlık (UTMOS + MOS), P50/P95 TTFA histogramı, SECS CDF, kategori başına CER, başarısızlık modu vurguları (kod-karıştırmalı istemler X%'de başarısız oldu) içeren sürüm notu.
