---
name: obs-platform-wiring
description: Bir observability platform (Langfuse, Phoenix, Opik, Datadog) seç ve trace + eval + prompt versiyonlarını mevcut bir agent'a bağla.
version: 1.0.0
phase: 14
lesson: 24
tags: [observability, langfuse, phoenix, opik, datadog, tracing]
---

Bir agent runtime ve ürün gereksinimleri verildiğinde, bir observability platform'u seç ve bağlantıyı iskele.

Karar:

1. Prompt management + session replay tek yerde gerekli -> **Langfuse**.
2. Derin RAG relevancy + drift/anomali tespiti gerekli -> **Phoenix**.
3. Otomatik prompt optimization + PII guardrail'leri gerekli -> **Opik**.
4. Zaten Datadog çalıştırılıyorsa -> **Datadog LLM Observability** (v1.37+ itibarıyla GenAI'yi native map'ler).
5. ELv2-free lisans gerekli -> **Langfuse** (MIT) veya **Opik** (Apache 2.0); saf OSS dağıtımı için Phoenix'ten kaçın.

Şunları üret:

1. OTel GenAI instrumentasyonu (Ders 23) — bu ortak substrate'tir.
2. Platform-spesifik SDK veya OTel exporter konfigürasyonu.
3. Domain'iniz için LLM-judge rubric'i (factual correctness, scope, tone, refusal quality).
4. Trace'lere bağlı prompt versiyonlama (Langfuse) veya trace clustering konfigürasyonu (Phoenix) veya experiment tanımları (Opik).
5. Loglanan içerik üzerinde guardrail'ler: PII redaction, secret scrubbing.
6. Dashboard'lar: session health, failure taxonomy, latency dağılımı, session başına maliyet.

Sert reject sebepleri:

- Eval'siz göndermek. Sadece tracing pahalı logging'tir.
- Harici doğrulama olmadan self-written LLM-judge kullanmak. CRITIC pattern (Ders 05): judge'lar factual grounding için harici tool'lara ihtiyaç duyar.
- Span body'lerinde PII depolamak. Her zaman harici store + reference ID'ler.

Refusal kuralları:

- Kullanıcı "her şey için tek platform" isterse, reddet ve yukarıdaki kararı sun. Hiçbir platform üç eksenin hepsinde baskın değildir.
- Ürünün her agent task'ı için acceptance criteria'sı yoksa, eval göndermeyi reddet. LLM-judge rubric'e ihtiyaç duyar; rubric ürün kararlarına ihtiyaç duyar.
- Kullanıcı "sampling yok, her şeyi yakala" isterse, reddet. Trace hacmi trafikle doğrusal ölçeklenir; ölçekte sampling (head-based veya tail-based) zorunludur.

Çıktı: `instrumentation.py`, `judge.py`, `dashboards.md`, platform seçimini, rubric'i, sampling stratejisini ve incident response'u açıklayan `README.md`. Ders 30'a (eval-driven development) veya Ders 26'ya (failure-mode taxonomy) işaret eden bir "sırada ne okumalı" ile bitir.
