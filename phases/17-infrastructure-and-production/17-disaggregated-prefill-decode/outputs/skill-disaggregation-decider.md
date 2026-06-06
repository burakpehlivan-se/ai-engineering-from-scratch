---
name: disaggregation-decider
description: Belirli bir iş yükü ve küme (cluster) için ayrıştırılmış prefill/decode (Dynamo veya llm-d) benimsenip benimsenmeyeceğine karar ver. Prefill:decode oranlarını, KV aktarım maliyetini ve beklenen tasarrufu nicelleştir.
version: 1.0.0
phase: 17
lesson: 17
tags: [disaggregated-serving, dynamo, llm-d, nixl, kv-transfer, prefill-decode]
---

İş yükü profili (istem/çıktı uzunluğu dağılımı, model, eşzamanlılık), küme topolojisi (GPU'lar, fabric, RDMA kullanılabilirliği) ve mevcut servis maliyetine göre bir ayrıştırma kararı üret.

Üretilecekler:

1. **Ayrıştırılsın mı?** Sayılı gerekçeyle Evet / Hayır. Taban çizgisi: istemler > 512 VE çıktılar > 200. Fabric: RDMA kullanılabilirliği yardımcı olur; yalnızca TCP, başa-baş noktasını uzatır.
2. **Yığın seçimi.** NVIDIA Dynamo (vLLM/SGLang/TRT-LLM üstünde yönetilen orkestratör) veya llm-d (Kubernetes-native Services). Operasyonel bağlama göre eşle.
3. **Prefill:decode oranı.** Dynamo Planner Profiler çıktılarını kullan veya iş yükü şeklinden hesapla (prefill TFLOPS'a karşı decode bayt/saniye). Örnek: RAG-ağırlıklı için 2 prefill : 1 decode; çıktı-ağırlıklı için 1:2.
4. **KV aktarım planı.** Adlandırılmış taşıma (NIXL over InfiniBand / RDMA / TCP yedek). İstem P99'un için istek başına aktarım vergisini hesapla.
5. **Yönlendirici entegrasyonu.** Önbellek-farkında yönlendirici (cache-aware router) (Phase 17 · 11) önde olmalı — önek eşleştirmesi olmadan ayrıştırma, önbellek kazanımını yitirir.
6. **Beklenen tasarruf.** Aynı yerdeki (colocated) taban çizgisine karşı hesapla; yayınlanmış vakayı (aynı SLA'da %30-40) göster.

**Hard rejects (zorunlu redler):**
- Kısa-istem iş yüklerini (<512 token) ayrıştırmak. Reddet — aktarım vergisi baskın çıkar.
- Önbellek-farkında yönlendirici olmadan dağıtmak. Reddet — kör yönlendirme KV yerelliğini sıfırlar.
- Topolojiyi yok saymak (raf paketlemesi). Reddet — aynı rafta RDMA'dan çok çoklu-raf atlama atlama üzerinden KV aktarımı daha pahalıya mal olur.

**Reddetme kuralları:**
- Kümenin < 4 GPU'su varsa reddet — ayrıştırmanın kâr getirmesi için yeterli havuz çeşitliliği yok.
- RDMA/InfiniBand yoksa ve plan da yoksa, TCP'nin başa-baş noktasını istemler >2K'ya çıkardığını not al; yeniden değerlendir.
- Ekip rol başına ölçeklendirmeyle iki GPU havuzunu işletemiyorsa, llm-d'yi reddet ve yönetilen alternatif olarak Dynamo'yu zorunlu kıl.

**Çıktı:** Ayrıştırma E/H, yığın seçimi, oran, taşıma, yönlendirici, beklenen tasarruf içeren tek sayfalık bir karar. Doğrulamak için tek bir metrikle bitir: KV aktarım P99 gecikmesi; plana özgü eşiği aşması durumunda kapıyı kapat.
