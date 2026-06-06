---
name: eval-report
description: Tam bir üretken model değerlendirmesi planla: örnek kalitesi, bağlılık, tercih, başarısızlık denetimi
version: 1.0.0
phase: 8
lesson: 14
tags: [değerlendirme, fid, clip, elo]
---

Yeni bir üretken model kontrol noktası, referans temel çizgisi ve modalite (görüntü / video / ses / 3B) verildiğinde, tam bir değerlendirme planı üret:

1. Örnek kalitesi. Ayrılan gerçek kümeye karşı 10-30k örnek üzerinde FID / FD-DINO / CMMD. Eşleşen çözünürlük. 3-tohum ortalama +/- std raporla.
2. Bağlılık. İstem-görüntü çiftlerinde CLIP skoru / CMMD. Metin-üstü-görüntü için HPSv2 + ImageReward + PickScore dahil et. Video için, görme-dil metrikleri (V-Eval) ekle. Ses için CLAP + MOS.
3. İkili tercih. Temel çizgiye karşı 200-2000 istemde kör A/B. İnsan + LLM-hakem + PartiPrompts kapsamı.
4. Kategori dağılımı. İstem kategorisi başına performans (insanlar, hayvanlar, metin render, kompozisyon, stil). Genel metrikler iyileşse bile kategori başına gerilemeleri işaretle.
5. Güvenlik / kötüye kullanım. NSFW sınıflandırıcı, deepfake algılayıcı, filigran kontrolü, en iyi-K jenerasyonlarda telif benzerlik taraması.
6. Onay. Açık geçit: FID temel çizgisinin +%5'i içinde VEYA >%55 insan kazanma oranı VEYA belgelenmiş niteliksel avantaj. Tek metrik iddiaları yok.

N < 5000'de FID raporlama. Modelin eğitimde görmüş olabileceği istemlerde hesaplanan kıyaslamaları gönderme. İnsan çapraz kontrolü olmadan yalnızca LLM-hakem sonuçlarını raporlama. Mutlak temel değeri ve tek bir tohumu raporlamadan "metrik %20 arttı" şeklindeki herhangi bir iddiayı işaretle.
