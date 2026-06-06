---
name: workflow-picker
description: Verilen bir task için doğru pattern'i (prompt chain, router, parallel, orchestrator-workers, evaluator-optimizer veya full agent) seç ve minimal implementasyonu üret.
version: 1.0.0
phase: 14
lesson: 12
tags: [anthropic, workflows, agents, patterns, minimal]
---

Bir task açıklaması verildiğinde, uyan en minimal pattern'i seç ve en küçük doğru implementasyonu üret.

Karar ağacı:

1. Adımları sıralayabilir misin? -> **prompt chain** veya **routing**.
2. Çıktının bağımsız çalıştırmalardan toplanması mı gerekiyor? -> **parallelization** (sectioning veya voting).
3. Üyelikleri task'a göre değişen bir specialist havuzuna mı ihtiyacın var? -> **orchestrator-workers**.
4. Bir judge geçene kadar iterative refinement mı gerekiyor? -> **evaluator-optimizer** (Self-Refine şekli).
5. Hiçbiri değilse, veya adım sayısı ara sonuçlara mı bağlı? -> **agent loop** (Ders 01).

Şunları üret:

- Workflow'lar için: LLM + tool çağrılarını birleştiren saf fonksiyonlar. Framework yok.
- Agent'lar için: Ders 01'den ReAct loop'u artı task'ın gerektirdiği tool registry.
- Karar gerekçesini, adım sayısını, beklenen token maliyetini ve gözlemlenebilir başarı kriterini içeren bir `README.md`.

Sert reject sebepleri:

- Task 3 adımlık bir prompt chain olduğunda bir framework'e (LangGraph, AutoGen, CrewAI) yönelmek. Aşırı mühendislik asıl problemi gizler.
- 3 çalışanlı bir orchestrator-worker'ı "multi-agent" olarak tanımlamak. Worker'lar agent değil, LLM çağrılarıdır. Açıklık için "orchestrator-workers" kullan.
- Durdurma koşulu olmayan evaluator-optimizer. `max_iter` ve "fail-pass-through" fallback'i olmadan, loop süresiz olarak dönebilir.

Refusal kuralları:

- Kullanıcı task aslında bir router olduğunda "multi-agent" isterse, reddet ve yeniden adlandır. Multi-agent etiketi operasyonel maliyet (koordinasyon, debugging, eval) taşır; routing'e bunlar gerekmez.
- Kullanıcı açık-uçlu bir araştırma task'ı için workflow isterse, reddet ve bir turn budget'lu agent öner. Workflow'lar öngörülebilir yörüngeler içindir.
- Kullanıcı 2 adımlık bir task için agent isterse, reddet ve prompt chaining öner. Agent'lar gecikme ve başarısızlık modu ekler; sadece ihtiyacın olduğunda kullan.

Çıktı: pattern seçimi + minimal kod + README. Durable state önemliyse Ders 13'e (LangGraph), handoffs ve guardrails için Ders 16'ya (OpenAI Agents SDK) veya yine de agent seçiyorsan Ders 01'e işaret eden bir "sırada ne okumalı" ile bitir.
