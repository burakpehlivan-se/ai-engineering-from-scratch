---
name: mtp-planner
description: Yeni bir ön-eğitim çalıştırması için çoklu token tahmini (multi-token prediction) entegrasyonu planlayın.
version: 1.0.0
phase: 10
lesson: 18
tags: [mtp, multi-token-prediction, deepseek-v3, pre-training, speculative-decoding]
---

Bir ön-eğitim çalıştırması belirtimi (model ölçeği, gizli boyut, katmanlar, veri token bütçesi, GPU topolojisi, hedef dağıtım) ve belirtilen bir hedef (daha yoğun eğitim sinyali vs spekülatif kod çözme taslağı vs her ikisi) verildiğinde, bir MTP entegrasyon planı üretin.

Şunu üretin:

1. Derinlik D. 1 veya 2 arasından seçin. DeepSeek-V3 D=1 kullanır ve ilk derinlikteki spekülatif kod çözme kabul oranını %80+ olarak bildirir. D=2, çoğu çalıştırma için azalan getiri bölgesidir. Hesaplama bütçesine karşı seçimi gerekçelendirin — her ekstra derinlik, eğitim adımı başına kabaca bir transformer bloğu hesaplama ekler.
2. Lambda programı. Varsayılan: eğitimin ilk %10'u için 0.3, sonrasında 0.1. Daha yoğun sinyalin daha önemli olduğu küçük modellerde (7B'nin altı) erken dönemde 0.5'a kadar ayarlayın; MTP kaybının ana kayba baskın olduğunu gözlemlerseniz aşağı ayarlayın.
3. Parametre bütçesi. Modül başına parametre sayısını ana modele göre raporlayın. Ek yükün ana parametrelerin %5'inin altında (yoğun) veya %3'ünün altında (MoE) olduğunu doğrulayın.
4. Bellek ve hesaplama ek yükü. Adım başına ekstra ileri geçiş FLOP'larını (kabaca `D * transformer_blok_maliyeti`), ekstra geri geçiş belleğini (D modülü için aktivasyon belleği) ve ekstra pik VRAM'ı (paylaşılan embedding ve kafa sayılmaz, projeksiyon ve transformer bloğu sayılır) nicelendirin.
5. Çıkarım zamanı kablolaması. MTP modülünün çıkarımda spekülatif kod çözme taslağı olarak nasıl tüketileceğini açıklayın. Leviathan kural entegrasyon yolunu ve KV geri alma defter tutma (bookkeeping) yöntemini adlandırın. Hedef çıkarım yığınıyla (vLLM, SGLang, TensorRT-LLM) uyumluluğu doğrulayın.

Sert redler:
- MTP olmadan önceden eğitilmiş yoğun bir modele MTP eklemek. Sonradan eklenemez — MTP modülleri eğitilmemiştir.
- İlk entegrasyon için D > 2. D=1 üzerindeki kazanç küçüktür; karmaşıklık hızla büyür.
- 1B aktif parametrenin altındaki bir modelde MTP. Sinyal, o ölçekte ek yük maliyetinden daha zayıftır.
- Hedef spekülatif kod çözme olduğunda paralel (Gloeckle tarzı) kafaları kullanmak. Nedensel olarak zincirleme yapmazlar.

Reddetme kuralları:
- Ön-eğitim verisi kısa diziler (2k'nin altı) tarafından domine ediliyorsa, reddedin. MTP kazanımları, derinlik-2 denetiminin önemli olduğu kadarıyla uzun diziler varsayar.
- Hedef çıkarım yığını hiç spekülatif kod çözmeyi desteklemiyorsa, MTP'nin yine de daha yoğun eğitim sinyalini satın aldığını not edin ve devam edin, ancak uyumsuzluğu işaretleyin.
- Kullanıcı MTP olmadan mevcut yoğun bir kontrol noktası üzerinde ön-eğitime devam ediyorsa, reddedin ve MTP'yi yalnızca temiz bir eğitim çalıştırmasının başında veya temiz bir veri sınırı sıfırlamasında eklemeyi önerin.

Çıktı: D, lambda programı, parametre ek yükünü (mutlak ve yüzde), hesaplama ek yükünü (eğitim adımı başına yüzde) ve çıkarım zamanı spekülatif kod çözme kablolama planını listeleyen tek sayfalık bir entegrasyon planı. MTP'yi tutmayı gerekçelendiren ölçülen metriği adlandıran bir "başarı kriteri" paragrafıyla bitirin: 50B eğitim tokeninden sonra derinlik 1'de kabul oranı %70'in üzerinde olmalıdır, aksi takdirde mimari geri döndürülmelidir.
