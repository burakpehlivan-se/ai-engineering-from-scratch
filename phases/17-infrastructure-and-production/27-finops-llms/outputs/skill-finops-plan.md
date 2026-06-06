---
name: finops-plan
description: Bir LLM FinOps programı tasarla — atıf şeması (kullanıcı/görev/kiracı + dört token katmanı), üç-kademeli uygulama merdiveni ve birim metrik (çözülen başına maliyet / artefakt başına maliyet).
version: 1.0.0
phase: 17
lesson: 27
tags: [finops, cost-attribution, multi-tenant, kill-switch, unit-economics, rate-limit]
---

Ürün yüzeyi, kiracı katmanları, aylık harcama ve mevcut atıf durumu verildiğinde bir FinOps planı üret.

Üretilecekler:

1. **Atıf şeması.** Çağrı yerinde damgalanan `user_id`, `task_id`, `route`, `tenant_id`. Dört token-katmanı sayımı (istem / araç / bellek / yanıt). Telemetry-joiner kalıbı tercih edilir.
2. **Birim metrik.** Ürün sonuç metriğini tanımla — bilet başına maliyet, artefakt başına maliyet, agent görevi başına maliyet, oturum başına maliyet. Faturalama modeline bağla.
3. **Uygulama merdiveni.** Kiracı başına hız sınırı (pikin 2-3 katı), günlük harcama tavanı (sözleşmenin 1,5-3 katı), z-skoru > 4'te kill switch.
4. **Pano.** İlk 5 görünüm: bugün kiracı başına harcama, görev başına sonuç başına maliyet, kullanıcı başına dağılım, önbellek isabet oranı etkisi, model yönlendirme bölünmesi.
5. **Yığılmış optimizasyon denetimi.** Önbellek (Phase 17 · 14), toplu iş (Phase 17 · 15), yönlendirme (Phase 17 · 16), ağ geçidi (Phase 17 · 19) katmanlarının tümünün devrede olduğunu kontrol et. Eksik kolları işaretle.
6. **İnceleme kadansı.** Haftalık: en çok harcayanlar + anomaliler. Aylık: kiracı başına birim-ekonomi. Üç aylık: iş yüklerini interaktif/yarı/toplu olarak yeniden sınıflandır.

**Hard rejects (zorunlu redler):**
- Çağrı yerinde atıf olmadan yayınlamak. Reddet — geriye dönük etiketleme harcamaların ~%10-30'unu kaybeder.
- Tek-kovalı faturalama. Reddet — dört token-katmanı dökümü zorunlu.
- Z-skoru temeli olmayan kill switch. Reddet — kurmadan önce taban çizgisi istatistikleri zorunlu.

**Reddetme kuralları:**
- Ürünün < 10 kiracısı varsa, tam çok-kiracılı uygulamayı reddet — önce temel kiracı-başına atıf zorunlu.
- Maliyet/sonuç tanımsızsa, panoyu reddet — önce bir birim metrik seç.
- Herhangi bir tek kiracı toplam harcamanın >%40'ıysa, plan yayınlanmadan önce özel birim-ekonomi incelemesi zorunlu kıl.

**Çıktı:** Atıf şeması, birim metrik, uygulama merdiveni, pano, yığılmış optimizasyon denetimi, inceleme kadansı içeren tek sayfalık bir plan. Tek bir uyarıyla bitir: projeksiyona karşı günlük harcama; delta > %20 ise sayfa gönder.
