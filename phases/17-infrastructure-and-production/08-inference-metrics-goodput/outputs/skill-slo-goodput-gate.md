---
name: slo-goodput-gate
description: LLM dağıtımlarını verim yerine goodput üzerinde kapatan, P50/P90/P99 yüzdeleri ve belgelenmiş araç seçimi olan CI/CD-hazır bir kıyaslama tarifi üret.
version: 1.0.0
phase: 17
lesson: 08
tags: [inference-metrics, goodput, ttft, tpot, itl, slo, benchmarking]
---

İş yükü (model, donanım, hedef eşzamanlılık, kullanıcıya-dönük etkileşim türü — akışlı sohbet / tek-seferlik / ses / agent) verildiğinde CI/CD için goodput-tabanlı bir SLO kapısı üret.

Üretilecekler:

1. **SLO spesifikasyonu.** Üç eşik: TTFT P99 sınırı, TPOT P99 sınırı, E2E P99 sınırı. Etkileşim türünden savunulabilir değerler seç (akışlı sohbet: TTFT 500 ms, TPOT 25 ms, E2E 3 s; ses: TTFT daha sıkı 300 ms; agent: E2E daha gevşek 5 s).
2. **Kıyaslama tarifi.** Araç seçimi (LLMPerf veya GenAI-Perf — seçtiğini ve nedenini belirt). İstem dağılımı (girdi ve çıktı token'larının ortalaması + standart sapması). Eşzamanlılık taraması (hedefin %25, %50, %100, %150'si).
3. **Goodput hesabı.** Formül: üç kısıtı aynı anda karşılayan isteklerin oranı. Üretim için >= %99, kanarya için >= %95 hedefle.
4. **Yüzde-birlik raporlama.** Her metrik için P50, P90, P99 raporla (yalnızca ortalama asla). Ortalamaları yalnızca sağduyu kontrolü için not düş.
5. **Araç tuzağı notu.** Aracın ITL'ye TTFT'yi dahil edip etmediğini belirt. Ekipler-arası karşılaştırmadan önce tanımı sabitle.
6. **Kaplama mantığı.** Goodput >= hedef VE hedef eşzamanlılıkta ise CI geçer. %100 ve %150 eşzamanlılık arasında goodput 5 puandan fazla düşerse işaretle — yük-testi başlık payının eksik olduğunu gösterir.

**Hard rejects (zorunlu redler):**
- Yalnızca verim üzerinde kapı koymak. Reddet ve goodput zorunlu kıl.
- P99 olmadan ortalama raporlamak. Reddet.
- Araç adını ve araç sürümünü atlamak. Reddet.
- Yalnızca hedef eşzamanlılıkta kıyaslama yapmak; taramayı her zaman yap.

**Reddetme kuralları:**
- Kullanıcının yazılı bir SLO'su yoksa, reddet ve etkileşim türüne dayalı bir tane yaz.
- İstem dağılımı "bir döngüde özdeş istemler" ise, reddet — bu istem-tektipliği tuzağıdır. Gerçekçi sentetik zorunlu.
- Kıyaslama < 30 çalıştırma veya çalıştırma başına <100 istek ise, istatistiksel olarak yetersiz olarak reddet.

**Çıktı:** Eşikler, kıyaslama tarifi, araç seçimi, yüzde-birlik rapor şablonu ve CI geçer/kalır kuralı listeleyen tek sayfalık bir SLO kapısı spesifikasyonu. Bilinen zayıflığa bağlı olarak eşzamanlılık eğrisine karşı goodput, istem dağılımı hassasiyeti veya parçalı prefill açık/kapalı kuyruk karşılaştırmasından birini adlandıran bir "sırada ne ölçülecek" paragrafıyla bitir.
