---
name: diff-attention-integrator
description: Yeni bir ön-eğitim çalıştırmasına veya LoRA ince ayarına Diferansiyel Attention V2 eklemek için entegrasyon planı.
version: 1.0.0
phase: 10
lesson: 16
tags: [differential-attention, diff-transformer, long-context, flash-attention, pre-training, lora]
---

Bir model mimarisi (gizli, kafalar, KV kafaları, katmanlar, d_head), bir hedef bağlam uzunluğu, bir halüsinasyon veya uzun bağlam profili (mevcut değerlendirmelerinizdeki başarısızlık modları) ve bir eğitim bütçesi (mevcut tokenlar, GPU-saat) verildiğinde, DIFF V2 için bir entegrasyon planı üretin.

Şunu üretin:

1. Entegrasyon modu. Sıfırdan ön-eğitim, ortada eğitim mimari değişimi veya Q projeksiyonlarında LoRA ince ayarı. Eğitim bütçesine ve mevcut ağırlıklara karşı seçimi gerekçelendirin.
2. Mimari farkı. Somut alan alan değişiklik listesi: hangi projeksiyonlar büyür, hangileri aynı kalır, hangi parametre sayısını ekliyorsunuz ve çıkarma (subtraction) attention bloğunda nereye yerleştirilir. Katman derinliğine göre `lambda_init` programını dahil edin (`0.8 - 0.6 * exp(-0.3 * (derinlik - 1))` makalenin varsayılanıdır; katman bazında telemetri instabilite gösterirse derinliğe göre ayarlayın).
3. Çekirdek seçimi. V2'nin kafa sayısı iki katına çıkması göz önüne alındığında FlashAttention 2 veya 3 desteğini doğrulayın. Kullanıcı tekrarlanabilirlik için açıkça ihtiyaç duymadıkça V1'in özel çekirdek yolunu reddedin.
4. Bellek bütçesi. KV cache temel seviyede kalır (KV kafaları değişmez). Token başına aktivasyon belleği deltasını hesaplayın (ek Q kafaları, ek hesaplama). Hedef bağlamda mutlak sayıları raporlayın.
5. Eğitim stabilite planı. İzlenecek şeyleri açıklayın: katman başına `lambda` sapması, kafa başına attention entropisi, Q projeksiyonları üzerinde gradyan varyansı. Telemetri diverjans gösterirse temel attention'a geri dönüşü tetiklemesi gereken belirli metriği adlandırın.

Sert redler:
- Devam eden ön-eğitim olmadan önceden eğitilmiş bir modele DIFF attention eklemek. Çıktı dağılımları sapar — düşür-ve-değiştir (drop-in) bir düzeltme değildir.
- Nisan 2026'dan sonra herhangi bir yeni çalıştırma için DIFF V1. V2, ölçülen tüm boyutlarda kesinlikle daha iyidir.
- Aynı zamanda uzun bağlam eğitim verisini etkinleştirmeden DIFF'i entegre etmek. Fayda yalnızca 32k'nin ötesinde görünür.
- Kontrollü bir deney olmadan `lambda_init`'i negatif bir değere değiştirmek. Negatif başlatma, gürültü tabanından fazlasını çıkarır ve eğitimi çökertebilir.

Reddetme kuralları:
- Hedef bağlam 16k'nin altındaysa, entegrasyonu reddedin ve standart attention'ı önerin. Eklenen parametre maliyeti, gürültü tabanı argümanıyla gerekçelendirilmez.
- Kullanıcı uzun bağlam değerlendirme verisi (RULER, needle-in-haystack, MultiNeedle) sağlayamıyorsa, reddedin ve önce kalibrasyon verisi isteyin.
- Kullanıcı FlashAttention-2 öncesi bir yığın üzerindeyse, reddedin ve entegrasyonu denemeden önce yığını yükseltmesini önerin.

Çıktı: Modu, parametre sayısı deltasını, KV cache etkisini, FlashAttention onayını, `lambda` programını ve 3 metriklik bir izleme panelini listeleyen tek sayfalık bir entegrasyon planı. DIFF V2'yi mimaride tutmaya karşı geri döndürmeye karşı kararı gerekçelendirecek belirli uzun bağlam değerlendirme sayısını (RULER 64k veya eşdeğerinde yüzde puanı deltası) adlandıran bir "başarı kriteri" paragrafıyla bitirin.
