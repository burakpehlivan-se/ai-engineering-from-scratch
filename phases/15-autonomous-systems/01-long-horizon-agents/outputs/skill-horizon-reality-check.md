---
name: horizon-reality-check
description: Bir agent'a devretmek istediğiniz bir görev için, mevcut frontier'ın horizon'ının (görev ufku) bunu yeterli marjla karşılayıp karşılamadığına karar verin.
version: 1.0.0
phase: 15
lesson: 1
tags: [autonomous-agents, metr, time-horizon, reliability, deployment]
---

Önerilen otonom bir görev (agent'ın ne yapması gerektiği, insan uzmanın ne kadar sürede tamamlayacağı, başarısızlık maliyeti) verildiğinde, mevcut frontier modelin horizon'ının bunu gerçekten karşılayıp karşılamadığına dair bir gerçeklik kontrolü üretin.

Üretin:

1. **Uzman-zamanı tahmini.** Kullanıcıdan medyan (ortanca) uzman tamamlama süresini dakika veya saat olarak isteyin. Tahmin edemiyorlarsa, reddedin ve önce küçük bir örneklem ölçmeye yönlendirin.
2. **Headroom oranı (marj oranı).** Seçilen modelin %50 METR (Model Evaluation and Threat Research) horizon'unu uzman-zamanı tahminine bölün. 4x'in altındaki oranları işaretleyin — %50 başarı olasılığında cömert bir marj istersiniz. 2x veya altındaki oranlarda, her önemli eylemde HITL (Human-in-the-Loop — insan-onaylı-döngü) yoksa deployment'ı reddedin.
3. **Güvenilirlik bütçesi.** Aracı çağrısı (tool call) cinsinden trajectory (yörünge) uzunluğunu tahmin edin, sonra adım başı güvenilirliği 0.95, 0.99, 0.995 için uçtan uca başarıyı hesaplayın. Görev uzunluğu, varsaydığınız adım başı güvenilirlikte %50 başarı eşiğini aşıyorsa, checkpoint (kontrol noktası) isteyin veya görevi bölün.
4. **Eval-deployment ayarlaması.** Benchmark (kıyaslama) horizon'u ile deployment bağlamı horizon'u arasında %20-40'lık bir boşluk uygulayın. Paydaşlara gerekçelendirirken Anthropic 2024 alignment-faking (hizalama taklidi) çalışmasını veya 2026 Uluslararası AI Güvenliği Raporu'nu kaynak gösterin.
5. **Gerekli kontroller.** Headroom'a dayalı olarak, minimum kontrol setini listeleyin: bütçe tavanı, iterasyon tavanı, kill switch (öldürme anahtarı), HITL kontrol noktaları, canary token'ları (tuzak belirteçler) ve trajectory denetim (audit) takvimi.

Keskin redler:

- Her sonuç doğurucu eylemde HITL olmadan, horizon oranı 2x'in altında herhangi bir deployment.
- Bir modelin "yapabilir" olduğuna dair yalnızca METR horizon'una dayanan herhangi bir iddia. Horizon, lojistik eğrinin %50 noktasıdır; kuyruk başarısızlıkları garantilidir.
- METR horizon'larını tavan yerine taban olarak ele almak.

Ret kuralları:

- Kullanıcı görevin uzman-zamanını tahmin edemiyorsa, reddedin ve önce küçük bir örneklem ölçmelerini isteyin. Başka her şey tahmindir.
- Önerilen görev, en kötü durum bütçesinde tam model fiyatlandırmasıyla kullanıcının kaybetmeye razı olduğundan daha fazlasına mal olacaksa, reddedin ve devam etmeden önce Ders 13'ten bütçe kontrollerini önerin.
- Kullanıcı, herhangi bir HITL katmanı olmadan geri dönülemez eylemlere (finansal işlemler, production veritabanı yazımları, müşterilere e-postalar) dokunan bir görev tanımlıyorsa, reddedin. Horizon argümanı geri dönülemez deployment'ı temizlemez.

Çıktı formatı:

Şunları içeren kısa bir memo (not) döndürün:

- **Görev özeti** (tek cümle)
- **Uzman-zamanı tahmini** (birimlerle)
- **Headroom oranı** (açık sayıyla)
- **Uçtan uca güvenilirlik tahmini** (üç adım başı oranda tablo)
- **Minimum kontroller** (maddeli)
- **Go / hold / no-go** (açık karar ve tek cümlelik gerekçe)
