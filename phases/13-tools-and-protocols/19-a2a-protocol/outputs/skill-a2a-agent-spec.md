---
name: a2a-agent-spec
description: A2A üzerinden çağrılabilir olması gereken bir agent için Agent Card ve skills schema'sını üret.
version: 1.0.0
phase: 13
lesson: 18
tags: [a2a, agent-card, task-lifecycle, delegation]
---

Bir agent'ın capability'leri ve hedeflenen collaborator'ları verildiğinde, onun A2A Agent Card'ını ve skill tanımlarını üret.

Şunları üret:

1. Agent Card. `name`, `description`, `url`, `version`, `schemaVersion`, `capabilities` (streaming, pushNotifications), `skills[]`.
2. Skills listesi. Her biri `id`, `name`, `description`, `inputModes`, `outputModes` ile. Description'larda "X durumunda kullan. Y için kullanma." desenini kullan.
3. Task-state planı. Her skill için beklenen state geçişleri ve input_required yolları.
4. Imzalama planı. Card'ın AP2 ile imzalanıp imzalanmayacağı (dışarıdan çağrılabilir agent'lar için önerilir).
5. Transport. HTTP üzerinden JSON-RPC (varsayılan) veya gRPC. v1.0 ile geriye dönük uyumluluğu not et.

Sert reject sebepleri:
- Kararlı bir URL'i olmayan herhangi bir Agent Card. Discovery'yi bozar.
- Input ve output mode'ları deklare edilmemiş herhangi bir skill. Çağıranlar uyumluluk hakkında muhakeme yapamaz.
- AP2 imzalama planı olmayan herhangi bir dışarıdan çağrılabilir agent. Impersonation vektörü.

Refusal kuralları:
- Agent'ın kullanım durumu tek bir tool çağrısı ise, A2A iskeleti kurmayı reddet; MCP öner.
- Agent açığa çıkarmaması gereken iç bileşenleri (tool call trace'leri, chain-of-thought) açığa çıkarıyorsa, reddet ve opaklığı zorunlu kıl.
- Agent'ın ödemeler için A2A'ya ihtiyacı varsa (AP2 kullanım durumu), AP2 extension sürümünü doğrula ve AP2'nin core A2A'dan ayrı olduğunu işaretle.

Çıktı: tek sayfalık bir Agent Card JSON'u, her operation için bir skills schema'sı, state-transition planı, imzalama ve transport seçimleri. Agent'ın söz verdiği minimum v1.0 geriye dönük uyumluluk garantisiyle bitir.
