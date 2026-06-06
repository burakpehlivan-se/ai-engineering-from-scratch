---
name: gpu-autoscaler-plan
description: Kubernetes-tabanlı bir LLM servis kümesi için üç-katmanlı bir GPU otomatik ölçekleme planı (Karpenter + KAI Scheduler + uygulama sinyalleri) tasarla. DCGM_FI_DEV_GPU_UTIL tuzaklarını ve kısmi tahsis başarısızlıklarını teşhis et.
version: 1.0.0
phase: 17
lesson: 03
tags: [kubernetes, gpu, autoscaling, karpenter, kai-scheduler, hpa, dynamo-planner, llm-d]
---

Küme topolojisi (düğümler, GPU türleri, NVLink alanları), iş yükü şekli (TP/PP yapılandırması, ortalama eşzamanlılık, patlama faktörü) ve SLO (TTFT P99, goodput) verildiğinde üç-katmanlı bir otomatik ölçekleme planı üret.

Üretilecekler:

1. **Katman 1 — Karpenter NodePool.** `instance-type`, `capacity-type` (on-demand / spot / reserved), `consolidationPolicy` (GPU havuzları için `WhenEmpty` ve `consolidateAfter: 1h` olmalı), GPU-dışı iş yüklerini dışlayan taint'leri ve KAI Scheduler seçimi için etiketleri belirt.
2. **Katman 2 — KAI Scheduler politikası.** Gang zamanlamanın gerekli olup olmadığını belirt (TP/PP > 1 için evet). Topoloji kısıtını tanımla (NVLink alanı, raf, bölge). Üretim ve eğitim kiracıları için kuyruk hiyerarşisini ve önceleme kurallarını belirt.
3. **Katman 3 — Uygulama otomatik ölçekleyicisi.** Sinyali seç: prefill-bağlı iş yükleri için kuyruk derinliği, decode-bağlı için KV önbellek kullanımı, karma için bileşik goodput. `DCGM_FI_DEV_GPU_UTIL`'i yasakla ve nedenini açıkla.
4. **Ayrıştırılmış bölünme.** Phase 17 · 17 ayrıştırılmış prefill/decode kullanılıyorsa, ayrı HPA'ları belirt — prefill havuzu için kuyruk derinliği sinyali, decode havuzu için KV kullanım sinyali.
5. **Sıcak havuz boyutlandırması.** SLO-kritik yollar için asgari hazır kopyalar; P99 TTFT kısıtına ve gözlemlenen soğuk başlangıç süresine (düğüm sağlama + model yükleme) dayalı.
6. **İzleme.** Panoya gönderilecek metrikler: kopya başına kuyruk derinliği, kopya başına KV kullanımı, düğüm sağlama bekleme süresi, gang-zamanlama erteleme sayısı, Karpenter konsolidasyon olayları.

**Hard rejects (zorunlu redler):**
- `DCGM_FI_DEV_GPU_UTIL` üzerinde HPA önermek. Reddet ve doğru sinyaller olarak kuyruk derinliği + KV kullanımını adlandır.
- Bir GPU havuzu için `consolidationPolicy: WhenEmptyOrUnderutilized` bırakmak. Reddet ve çalışan-iş-çıkarma riskini göster.
- Bir TP/PP iş yükü için gang zamanlamayı yok saymak. Reddet — kısmi tahsis $-yakan bir anti-kalıptır.

**Reddetme kuralları:**
- Kümenin yalnızca bir GPU türü ve bir düğümü varsa, Karpenter önerme — müşterinin önce yönetilen serverless'a (Phase 17 · 02) ihtiyacı var.
- Operatör "GPU belleğine göre ölçekle" diye soruyorsa, reddet — vLLM `--gpu-memory-utilization`'a kadar önceden tahsis eder; bellek bir istekte bile %90 civarında kalır.
- Gang zamanlama bir TP-8 iş yükü için karmaşıklık gerekçesiyle reddedilirse, planı onaylamayı reddet — 8 dağınık GPU üzerinde tek-pod yerleşimi atomik olarak başarısız olur.

**Çıktı:** Bir Karpenter YAML parçacığı, bir KAI Scheduler yapılandırma parçacığı, bir HPA/özel otomatik ölçekleyici sinyal seçimi, bir sıcak havuz sayısı ve beş pano metriği içeren tek sayfalık bir plan. Tek bir kill-switch ile bitir: P99 TTFT ihlal ederse, bilinen son otomatik ölçekleyici durumuna geri dön.
