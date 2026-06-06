---
name: ab-plan
description: Bir LLM A/B testi tasarla — platformu (Statsig veya GrowthBook), birincil metriği, guardrail'leri, LLM-gürültü-arabellekli örneklem büyüklüğünü, CUPED'i, sıralı durdurmayı ve çoklu-karşılaştırma düzeltmesini seç.
version: 1.0.0
phase: 17
lesson: 21
tags: [ab-testing, statsig, growthbook, cuped, sequential, benjamini-hochberg, srm]
---

Özellik değişikliği (istem / model / üretim parametresi), taban çizgisi metrikleri, beklenen kaldıraç (lift) ve ekip duruşu (warehouse-native OSS veya paketlenmiş SaaS) verildiğinde bir A/B planı üret.

Üretilecekler:

1. **Platform.** Statsig (paketlenmiş SaaS, OpenAI'ye ait) veya GrowthBook (MIT OSS, warehouse-native). Gerekçelendir.
2. **Birincil metrik + guardrail'ler.** Birincil, hareket ettirmeye çalıştığın metriktir; guardrail'ler gerilememesi gereken metriklerdir (istek başına maliyet, gecikme P99, reddetme oranı).
3. **Örneklem büyüklüğü.** Klasik güç hesaplaması × 1.4 (LLM deterministik-olmama arabelleği).
4. **Tasarım.** Sabit-ufuk veya sıralı. Güçlü sinyaller bekleniyorsa sıralı; değişiklik süssüz ise sabit.
5. **CUPED.** Birincil metrik için ön-dönem verisi varsa etkinleştir; regresörü belirt.
6. **Düzeltme.** Az sayıda test için Bonferroni; birçok ilişkili test için Benjamini-Hochberg.
7. **SRM.** Her deneyde SRM kontrolü zorunlu kıl; işaretlenirse durdur ve hata ayıkla.

**Hard rejects (zorunlu redler):**
- Sezgiselere dayanarak yayınlamak. Reddet — A/B veya belgelenmiş A/B-yok istisnası zorunlu.
- Aynı birincil metrik üzerinde >5 deneyi BH/Bonferroni olmadan çalıştırmak. Reddet — yanlış keşif kaçınılmaz.
- SRM kontrolünü atlamak. Reddet — atama hataları yaygındır.

**Reddetme kuralları:**
- Özellik için trafik < 1000 kullanıcı/hafta ise, sabit A/B'yi reddet — bunun yerine gölge + kanarya (Phase 17 · 20) zorunlu kıl.
- Birincil metrik öznelse (ör. "kalite") ve nesnel bir vekil yoksa, paralel olarak insan değerlendirmesi zorunlu kıl.
- Kaldıraç hipotezi LLM gürültü tabanından küçükse, reddet — deney gerçekçi örneklem büyüklüğüyle onu algılayamaz.

**Çıktı:** Platform, birincil + guardrail'ler, örneklem büyüklüğü, tasarım, CUPED, düzeltme, SRM politikası içeren tek sayfalık bir plan. Karar kuralıyla bitir: birincil anlamlı + tüm guardrail'ler anlamlı-değil-negatif → yayınla; herhangi bir guardrail ihlali → birincil sonucu ne olursa olsun yayınlama.
