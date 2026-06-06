---
name: observability-stack
description: Yığın, ölçek, bütçe ve lisans duruşu verildiğinde bir LLM gözlemlenebilirlik yığını (geliştirme platformu + ağ geçidi + isteğe bağlı ölçek katmanı) seç ve OpenTelemetry GenAI öznitelik kümesini tanımla.
version: 1.0.0
phase: 17
lesson: 13
tags: [observability, langfuse, langsmith, phoenix, arize, helicone, opik, opentelemetry, genai-conventions]
---

Yığın (LangChain / DSPy / ham SDK), ölçek (iz/gün), bütçe, lisans duruşu (yalnızca MIT vs ticari OK) ve self-host gereksinimi verildiğinde bir gözlemlenebilirlik planı üret.

Üretilecekler:

1. **Geliştirme platformu seçimi.** Langfuse (OSS), LangSmith (LangChain-öncelikli ticari), Opik (Comet OSS) veya hiçbiri. Yığın ve lisansla gerekçelendir.
2. **Ağ geçidi/telemetri seçimi.** Helicone (proxy + ağ geçidi), SigNoz (tam APM), OpenLLMetry (saf OTel). Zaten bir AI ağ geçidi (Phase 17 · 19) kullanılıyorsa, entegrasyonu adlandır.
3. **Ölçek/göl katmanı.** İsteğe bağlı; uzun-vadeli analitik için Arize AX veya ham Iceberg, RAG sapması için Phoenix.
4. **OTel GenAI sözleşmeleri.** Asgari öznitelik kümesini belirt: `gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.request.temperature`, `gen_ai.response.finish_reasons`, artı kuruma-özgü (tenant_id, user_id, task).
5. **Örnekleme politikası.** %100 hatalar, %100 yüksek-maliyet (>$0.10/çağrı), N% başarı örnekleme oranı. Ham-saklama penceresi (14g / 30g / 90g). Toplamalar daha uzun saklanır.
6. **Uyarma.** Uyarıya sahip olması gereken beş metrik: hata oranı, P99 TTFT, istek başına maliyet, istem-önbellek isabet oranı, reddetme oranı.

**Hard rejects (zorunlu redler):**
- Bir OTel geri düşüşü olmadan çerçeveye-özgü SDK içinde enstrüman etmek. Reddet — çerçeve kilitlenmesi.
- Düzenlenmemiş bir iş yükü için Datadog-sınıfı fiyatlandırmayla >$500/ay'da izlerin %100'ünü tutmak. Reddet — örneklemeyi öner.
- OpenTelemetry GenAI sözleşmelerini yok saymak. Reddet — 2026 birlikte-çalışabilirlik onları gerektirir.

**Reddetme kuralları:**
- İz/gün > 5M ise ve ekip tam Datadog saklamada ısrar ediyorsa, maliyet tahmini olmadan reddet.
- Ekip yalnızca MIT ise ve LangSmith seçiyorsa, reddet — Langfuse MIT eşdeğeridir.
- Ekipte AI ağ geçidi yoksa ve Helicone'u ağ geçidi VE gözlemlenebilirlik olarak seçiyorsa, kabul et — proxy, ~500 RPS'ye kadar ağ geçidi olarak iki kat çalışır (Phase 17 · 19 ağ geçidi ölçeğini kapsar).

**Çıktı:** Geliştirme platformu, ağ geçidi, ölçek katmanı (varsa), OTel öznitelik kümesi, örnekleme kuralı, beş uyarı adlandıran tek sayfalık bir plan. Yığından sapmayı sinyallediği tek metrikle bitir: son 7 günde tam OTel GenAI özniteliklerine sahip LLM çağrılarının yüzdesi.
