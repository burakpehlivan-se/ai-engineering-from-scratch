---
name: agents-sdk-scaffold
description: Triage agent, handoff'lar, input/output/tool guardrail'leri, session store ve bir trace processor ile bir OpenAI Agents SDK app'i iskele.
version: 1.0.0
phase: 14
lesson: 16
tags: [openai, agents-sdk, handoffs, guardrails, tracing, session]
---

Bir ürün domain'i ve bir specialist agent listesi verildiğinde, bir OpenAI Agents SDK app'i iskele.

Şunları üret:

1. Specialist başına bir `Agent` artı sadece handoff'ları olan (domain tool'u olmayan) bir `triage` agent.
2. Tipli input schema, net açıklama (modele ne zaman kullanılacağını söyler) ve execution sandbox ile domain tool'u başına bir `FunctionTool`.
3. Triage'den her specialist'a `Handoff`. Tool adlarının `transfer_to_<agent>` kuralına uyduğunu doğrula.
4. PII, policy, scope için `InputGuardrail`. Guardrail LLM'i ana modele göre büyük olmadıkça default olarak parallel mode; büyükse blocking kullan.
5. Uzunluk, PII, policy için `OutputGuardrail`. Güvenlik-kritik çıktılar için prod'da her zaman blocking.
6. Network veya filesystem'a dokunan function tool'larında per-tool guardrail'ler.
7. `Session` store'u (default SQLite; prod için Redis).
8. Span'ları OpenAI'ın trace UI'ının yanında backend'inize bağlayan `add_trace_processor`.

Sert reject sebepleri:

- Domain tool'ları olan triage agent'lar. Triage sadece handoff yapar; karışımı router'ın kararını sulandırır.
- Input/output'u mutate eden guardrail'ler. Guardrail'ler onaylar veya reddeder — yeniden yazmaz.
- Sessiz handoff loop'ları. Bir hop counter (default max 3) zorunlu kıl.

Refusal kuralları:

- Kullanıcı "guardrail yok, sadece hızlı hareket et" isterse, ücretli kullanıcılara veya PII'a dokunan herhangi bir ürün için reddet.
- Ürün sadece 2 specialist içeriyorsa, triage+handoff'lar yerine doğrudan classifier ile `Agents` üzerinden routing öner (Ders 12) — daha az token maliyeti.
- Prod'da tracing devre dışıysa, gönderimi reddet. Multi-step başarısızlıklar trace olmadan debug edilemez.

Çıktı: `agents.py`, `tools.py`, `guardrails.py`, `app.py`, triage-agent gerekçesini, guardrail modlarını, trace processor'ı ve session backend'ini içeren `README.md`. Ders 23'e (OTel GenAI), Ders 24'e (observability backends) veya Claude Agent SDK çevirisi için Ders 17'ye işaret eden bir "sırada ne okumalı" ile bitir.
