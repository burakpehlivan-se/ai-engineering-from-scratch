---
name: otel-genai
description: Doğru attribute'lar ve opt-in content capture ile bir agent'ı OpenTelemetry GenAI semantic conventions ile instrument'la — invoke_agent, chat, tool_call span'ları.
version: 1.0.0
phase: 14
lesson: 23
tags: [opentelemetry, genai, observability, tracing, semantic-conventions]
---

Bir agent runtime verildiğinde, OTel GenAI semantic conventions'ı bağla.

Şunları üret:

1. Agent run'ı başına `invoke_agent` span'ı. Remote agent servisleri için Kind CLIENT, in-process için INTERNAL. Ad: `invoke_agent {gen_ai.agent.name}`.
2. `gen_ai.operation.name=chat`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model` ile LLM çağrısı başına `chat` span'ı.
3. `gen_ai.tool.name` ve uygulanabilir olduğunda `gen_ai.data_source.id` (RAG corpus / memory store) ile tool çağrısı başına `tool_call` span'ı.
4. Opt-in content capture: default OFF; ON olduğunda input/output'ları harici olarak depolar ve span'lerde `*.reference_id` kaydeder.
5. Context propagation: W3C trace context header'ları kullan, böylece multi-process run'lar (Claude Agent SDK CLI subprocess) tek bir trace'te birleşir.

Sert reject sebepleri:

- Default olarak tam prompt/output'ları inline yakalamak. PII ve secret sızıntısı riski; ayrıca spec'i ihlal eder.
- Eksik `gen_ai.provider.name`. Multi-provider dashboard'ları kırılır.
- Orphan tool span'ları. Her zaman active context üzerinden parent-child ilişkisi kur.

Refusal kuralları:

- Runtime process sınırları arasında context propagate edemiyorsa, reddet. Claude Agent SDK + CLI kullanıcıları için multi-process trace stitching zorunludur.
- Ürünün düzenleyici kısıtları varsa (HIPAA, GDPR), inline content capture'ı reddet. Sadece access control'lü harici store.
- Backend `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` set etmiyorsa, uyar: collector upgrade'inde attribute adları değişebilir.

Çıktı: `tracer.py`, `attributes.py`, `content_store.py`, span yapısını, stability opt-in'i ve content-capture policy'sini açıklayan `README.md`. Ders 24'e (backends: Langfuse, Phoenix, Opik) veya Claude Agent SDK trace-context propagation için Ders 17'ye işaret eden bir "sırada ne okumalı" ile bitir.
