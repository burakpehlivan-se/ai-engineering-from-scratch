---
name: otel-genai-instrumentation
description: Bir agent codebase'i için uçtan uca OTel GenAI span'ları yayma instrumentation planı üret.
version: 1.0.0
phase: 13
lesson: 19
tags: [otel, observability, gen-ai, tracing]
---

Bir agent codebase'i verildiğinde (LLM çağrıları, tool dispatch, MCP client, sub-agent'lar), bir OTel GenAI instrumentation planı üret.

Şunları üret:

1. Span hiyerarşisi. Root `agent.invoke_agent` (INTERNAL) ve çocuklar: `llm.chat` (CLIENT), `tool.execute` (INTERNAL), `mcp.call` (CLIENT), `subagent.invoke` (INTERNAL).
2. Span başına attribute kontrol listesi. `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.usage.*`, `gen_ai.tool.name`, `gen_ai.agent.name`.
3. Propagation kuralı. Her remote çağrıda W3C traceparent inject et; MCP stdio için ara bir alan olarak `_meta.traceparent` kullan.
4. Content capture policy. Varsayılan olarak kapalı; hangi env var'ın etkinleştirdiğini belgele; PII risklerini adlandır.
5. Exporter seçimi. Jaeger / Tempo / Langfuse / Phoenix / Datadog / Honeycomb; wire olarak OTLP.

Sert reject sebepleri:
- MCP veya sub-agent sınırları üzerinde trace propagation'ı eksik olan herhangi bir plan.
- Content capture'ı varsayılan olarak açık olan herhangi bir plan. Prompt'ları ve PII'yi sızdırır.
- `gen_ai.` veya açık vendor prefix olmadan keyfi custom attribute yayan herhangi bir plan.

Refusal kuralları:
- Codebase, built-in OTel auto-instrumentation'a sahip bir framework kullanıyorsa (Pydantic AI, LangGraph, AgentOps), önce framework hook'unu öner.
- Exporter backend on-prem ise ve ekibin SRE desteği yoksa, managed bir backend öner.
- Kullanıcı, prod'da debugging için content yakalamayı istiyorsa, tipli bir consent policy ve PII redaction pipeline'ı olmadan reddet.

Çıktı: span hiyerarşisi, span başına attribute kontrol listesi, propagation kuralı, content capture policy ve exporter seçimini içeren tek sayfalık bir plan. Alarm verilecek en önemli metrikle bitir (tipik olarak p95 `gen_ai.client.operation.duration`).
