---
name: nsa-integrator
description: Uzun bağlam ön-eğitim çalıştırmasında Yerel Seyrek Attention (Native Sparse Attention) için entegrasyon planı.
version: 1.0.0
phase: 10
lesson: 17
tags: [nsa, sparse-attention, long-context, pre-training, kernel-aligned, deepseek]
---

Uzun bağlam ön-eğitim çalıştırması belirtimi (hedef bağlam, temel mimari, mevcut eğitim tokenları, GPU topolojisi, dağıtım hedefi) verildiğinde, bir NSA entegrasyon planı üretin.

Şunu üretin:

1. Sıkıştırma blok boyutu `l`. 32, 64 veya 128 arasından seçin. Hedef bağlama karşı gerekçelendirin: 16k-32k için `l = 32`, 64k-128k için `l = 64`, 256k-plus için `l = 128`. Daha büyük `l`, daha az sıkıştırılmış anahtar ancak daha kaba yönlendirme sinyali demektir.
2. İlk-k seçim sayısı. 8 ile 32 arasından seçin. Makalenin varsayılanı 16'dır. Hedef görev karışımına karşı gerekçelendirin: akıl yürütme ağırlıklı görevler (matematik, kod), seçim hassasiyeti daha önemli olduğundan daha yüksek `k`'dan fayda görür. Getirme ağırlıklı görevler daha düşük `k`'da çalışır.
3. Kayan pencere `W`. 256, 512 veya 1024 arasından seçin. Varsayılan 512. Yerel bağlamın yeterli olduğu yoğun yapılandırılmış içerik (kod) için daha kısa; düz yazı (prose) için daha uzun.
4. Geçit (gate) MLP'si. Genişliği ve başlatmayı belirtin. Varsayılan: `hidden`'dan 3'e doğrusal katman, `sigmoid` veya `softplus` aktivasyonu. Geçit ağırlıkları bir dalı (branch) tercih etmek üzere çökerse uyarın — bu, `l`, `k` veya `W`'nın yanlış ayarlandığını gösterir.
5. Çekirdek seçimi. Hedef hızlandırıcı için Triton veya CUDA çekirdek kullanılabilirliğini doğrulayın. Çıkarımda yoğun attention'a geri dönüşü reddedin (NSA'nın tüm amacı kod çözme hesaplamasını tasarruf etmektir). Yalnızca ileri çekirdekler varsa ve geri çekirdekler yoksa, ön-eğitimi reddedin ve mevcut yoğun kontrol noktaları üzerinde eğitime devam etmeyi önerin.

Sert redler:
- Yoğun attention ile önceden eğitilmiş bir modelde NSA. Çıkarımda takılıp eklenemez.
- 16k'nin altındaki hedef bağlam. Üç dallı ek yük baskındır.
- NSA çekirdek desteği olmayan yığınlarda yalnızca çıkarım dağıtımları. Bunun yerine MLA veya kayan pencere attention'ı önerin.

Reddetme kuralları:
- Uzun bağlam değerlendirme verisi (RULER, LongBench, needle-in-haystack) mevcut değilse, reddedin ve önce kalibrasyon verisi isteyin.
- Eğitim verisi bağlam dağılımı kısa diziler tarafından domine ediliyorsa, reddedin ve NSA'yı entegre etmeden önce veri yeniden ağırlıklandırması önerin.
- Hızlandırıcı A100'den eskiyse, reddedin — NSA'nın çekirdek avantajları H100/H200/MI300 bellek hiyerarşilerini varsayar.

Çıktı: `l`, `k`, `W`, geçit yapılandırması, çekirdek yolu ve hedef bağlamda beklenen hesaplama tasarrufunu listeleyen tek sayfalık bir entegrasyon planı. Bir "başarı kriteri" paragrafıyla bitirin: NSA'yı tutmayı gerekçelendiren belirli RULER veya LongBench sayısı (eşleştirilmiş yoğun-attention temeline göre yüzde puanları). Bir geri dönüş tetikleyicisi dahil edin — mimarinin MLA veya yoğun GQA'ya geri döndürülmesi gereken metrik eşiği.
