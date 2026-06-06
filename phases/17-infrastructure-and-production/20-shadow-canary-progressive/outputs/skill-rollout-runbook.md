---
name: rollout-runbook
description: Yeni bir LLM modeli veya istem şablonu için gölge → kanarya → A/B → %100 yayılım planı tasarla; beş kanarya kapısı, gürültü-tabanı-farkında eşikler ve saniyeler-içinde geri alma yolu içersin.
version: 1.0.0
phase: 17
lesson: 20
tags: [rollout, canary, shadow, progressive-delivery, feature-flags, argo-rollouts, flagger, kserve]
---

Aday bir değişiklik (yeni model, yeni istem şablonu, yeni yönlendirici politikası), taban çizgisi üretim metrikleri ve risk toleransı verildiğinde, bir yayılım runbook'u üret.

Üretilecekler:

1. **Gölge planı.** Süre (24-72 saat). Kaydedilen metrikler: çıktılar, token sayıları, gecikme, reddetme, hata. Şunlarda uyar: >%20 maliyet kayması, >%30 çıktı uzunluğu kayması, herhangi bir şema ihlali.
2. **Kanarya ilerleyişi.** Aşamalar (%1 → %10 → %25 → %50 → %75 → %100). Aşama başına süre (30dk-24sa, trafik hacmine göre; istatistiksel güven için her aşamada yeterli veri olduğundan emin ol).
3. **Beş kapı.** Gecikme P99, istek başına maliyet, hata/reddetme, çıktı-uzunluğu P99, thumbs-down oranı için tam eşikleri belirt. Gürültü tabanının (değişmez %15 varyans beklentisi) üzerinde ayarla.
4. **Araçlar.** Yayılım denetleyicisini (Argo Rollouts, Flagger, KServe) ve anında geri alma için feature-flag sistemini adlandır.
5. **Geri alma yolu.** Üç eylemi belgele: flag'i çevir → sabitlenmiş digest'i geri al → doğrula. Hedef süre: uçtan uca 60 saniyenin altında.
6. **A/B atlanır mı?** Gerekçelendir. İyileştirilmiş-varyant değişiklikleri A/B'yi atlar; belirgin biçimde farklı değişiklikler (yeni davranış, yeni maliyet eğrisi) A/B gerektirir.

**Hard rejects (zorunlu redler):**
- Gölge modunu atlamak. Reddet — maliyet sıçramaları ve uzunluk regresyonları çevrimdışı değerlendirmenin arasından kayar.
- %15 varyanstan daha sıkı kapılar. Reddet — yanlış alarmlar meşru yayılımları durduracaktır.
- Yeniden dağıtım gerektiren geri alma. Reddet — bu bir geri alma değil, hasar raporudur.

**Reddetme kuralları:**
- Değişiklik güvenlik-açısından kritikse (ör. PII işleme değişikliği), ek bir açık kapı zorunlu kıl: kanaryaya başlamadan önce gölge örnekleminde sıfır PII sızıntısı.
- Trafik hacmi <100 istek/saat ise, uzatılmış kanarya aşamaları zorunlu kıl — aksi durumda kapı gürültüsü sinyali ezer.
- Ekip beş kanarya kapısı için taban çizgisi metrikleri sağlayamıyorsa, yayılımı reddet — taban çizgisi ön koşuldur.

**Çıktı:** Gölge, kanarya, kapılar, araçlar, geri alma, A/B duruşu içeren tek sayfalık bir runbook. Bir geri alma tatbikatı gerekliliğiyle bitir: ilk gerçek dağıtımdan önce geri almayı bir kez prova et.
