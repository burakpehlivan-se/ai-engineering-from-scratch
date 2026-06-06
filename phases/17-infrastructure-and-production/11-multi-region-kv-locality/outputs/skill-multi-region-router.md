---
name: multi-region-router
description: KV-önbellek yerelliği, ikametgâh sınırları, DR manifesti ve üç aylık bir yük-devretme tatbikatı içeren çok-bölgeli bir LLM yönlendirme planı tasarla.
version: 1.0.0
phase: 17
lesson: 11
tags: [multi-region, kv-cache, routing, dr, bedrock-cri, vllm-router, llm-d, gorgo]
---

Kapsamdaki bölgeler, ikametgâh sınırları, beklenen önek-önbellek çeşitliliği ve TTFT SLA verildiğinde çok-bölgeli bir yönlendirme ve DR planı üret.

Üretilecekler:

1. **Yönlendirici seçimi.** Önbellek-farkında yönlendiriciyi (vLLM Router, llm-d router) seç ve KV-olay kanalını açıkla. Önek-karma algoritmasını (ör. 512-token kayan) ve bağ-bozanı (en az kuyruk derinliği) belirt.
2. **Yönlendirme politikası.** Bölgesel-öncelikli veya küresel (GORGO-tarzı) prefill + RTT enküçüklemesi mi? İstem uzunluğu dağılımıyla gerekçelendir — uzun istemler (>8K token) bölgeler-arası yönlendirmeden yararlanır; kısa istemler yararlanmaz.
3. **İkametgâh bölümlemesi.** Herhangi bir optimizasyondan önce: yasal nedenlerle hangi istekler hangi bölgelere bağlı (GDPR, HIPAA). TTFT iyileşse bile bölgeler-arası-ikametgâh yönlendirmesini yasakla.
4. **Ticari CRI katmanı.** Kullanılabilirlik katmanı olarak Bedrock Cross-Region Inference veya GKE Multi-Cluster Gateway etkinleştirilip etkinleştirilmeyeceğini öner. Bu katmanın bir TTFT optimizasyonu OLMADIĞINI açıkça belirt.
5. **DR manifesti.** Üç-dosya asgari (HF deposu + motor yapılandırması + dağıtım manifesti). Tokenleştirici, kuantizasyon yapılandırmaları, RoPE, sohbet şablonları, LoRA adaptörlerinin dahil edildiğini doğrula. Depolamayı belirt (S3 bölgeler-arası çoğaltma, çok-bölgeli GCS).
6. **Yük-devretme tatbikatı.** Üç aylık kadans. Kim çalıştırır, ne ölçülür (RTO, RPO, önbellek ısınma süresi). Hedef: gerçek 2024 JPMorgan tatbikatıyla eşleşen 30 dakikalık RTO.

**Hard rejects (zorunlu redler):**
- Yönlendirme optimizasyonu için ikametgâhı yok saymak. Reddet — GDPR ihlali TTFT kazanımını yener.
- Bedrock CRI'nın bölgeler-arası yönlendirmeyi "çözdüğünü" iddia etmek. Reddet — CRI kullanılabilirliktir, TTFT değil.
- Yalnızca ağırlıkları yedeklemek. Reddet — %32 DR başarısızlık istatistiğini adlandır ve üç-dosya manifestini zorunlu kıl.

**Reddetme kuralları:**
- Kapsamda yalnızca bir bölge varsa, planı reddet — tek bölgenin farklı başarısızlık modları var (Phase 17 · 03 kapsar).
- İkametgâh ve TTFT SLA uyumsuzsa (ör. 8K istemlerde P99 TTFT < 100 ms ile AB ikametgâhının istek başına soğuk önek üzerinde prefill'i zorlaması), SLA vaat etmeyi reddet ve ürün gereksinimini yükselt.

**Çıktı:** Yönlendirici, yönlendirme politikası, ikametgâh bölümleri, CRI katmanı duruşu, DR manifesti, üç aylık tatbikat sahibi adlandıran tek sayfalık bir plan. Uyarı verilecek tek metrikle bitir: plana-özgü bir eşiğin altına düşen bölgeler-arası önek-önbellek isabet oranı.
