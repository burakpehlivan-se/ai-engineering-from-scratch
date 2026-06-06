---
name: crew-or-flow
description: Verilen bir task için CrewAI Crew veya Flow seç ve minimal implementasyonu iskele.
version: 1.0.0
phase: 14
lesson: 15
tags: [crewai, crews, flows, multi-agent, role-based]
---

Bir task açıklaması verildiğinde, Crew (autonomous) veya Flow (deterministik) seç, sonra iskele kur.

Karar:

1. Task'ın SLA, compliance veya deterministik replay gereksinimleri var mı? -> Flow.
2. Task keşifsel mi (research, first draft, brainstorm)? -> Crew.
3. Task 4+ specialist ve LLM'in seçtiği bir sıralama var mı? -> Hierarchical Crew.
4. Task sabit sırada <=3 specialist mi içeriyor? -> Sequential Crew veya Flow — Flow tercih et.

Crew'lar için şunları üret:

1. Agent tanımları: role, goal, backstory (sıkı, <=200 kelime), tools.
2. Task tanımları: description, expected_output, agent.
3. Doğru Process (Sequential | Hierarchical) ile bir Crew.
4. Crew'u örnek input'lar üzerinde çalıştıran ve expected_output'ların üretildiğini kontrol eden bir test harness.

Flow'lar için şunları üret:

1. `@start` entry fonksiyonu.
2. Bir DAG oluşturan `@listen(topic)` adımları.
3. Açık event topic'leri; sihirli broadcast yok.
4. Bir replay harness'i: bir kickoff payload'ı verildiğinde deterministik olarak yeniden çalıştırır.

Sert reject sebepleri:

- Backstory'si olmayan Crew'lar. Backstory'ler yük taşıyıcıdır.
- Açık topic adları olmayan Flow'lar. "Implicit chaining" audit amacını boşa çıkarır.
- 2 specialist ile Hierarchical Crew'lar. Manager overhead'i maliyeti hak etmiyor.

Refusal kuralları:

- Kullanıcı yalnızca production'a yönelik bir compliance task'ı için Crew isterse, reddet ve Flow'a geçir.
- Kullanıcı açık-uçlu bir araştırma task'ı için Flow isterse, reddet ve Crew'a geçir.
- Backstory 200 kelimeyi aşarsa, reddet ve kırpılmasını zorunlu kıl. Context bütçesi sonludur.

Çıktı: `agents.py`, `tasks.py`, `crew.py` veya `flow.py`, artı karar gerekçesini içeren `README.md`. Observability için Ders 24'e (Langfuse/AgentOps) veya Flow'un durable resume semantiğine ihtiyacı varsa Ders 13'e işaret eden bir "sırada ne okumalı" ile bitir.
