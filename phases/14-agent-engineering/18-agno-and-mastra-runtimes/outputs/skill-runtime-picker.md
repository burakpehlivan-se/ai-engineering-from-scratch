---
name: runtime-picker
description: Verilen bir stack, latency bütçesi ve operasyonel shape için bir production agent runtime (Agno, Mastra, LangGraph, provider SDK) seç.
version: 1.0.0
phase: 14
lesson: 18
tags: [agno, mastra, langgraph, runtime, selection]
---

Bir stack, bir latency bütçesi, gerekli primitive'ler ve bir operasyonel shape verildiğinde, bir runtime seç.

Karar:

1. Python + FastAPI + saniyede binlerce kısa-ömürlü agent -> **Agno**.
2. TypeScript + Next.js/Vercel + birleşik multi-provider -> **Mastra**.
3. Durable state, açık graph, resume-on-failure -> **LangGraph** (Ders 13).
4. Claude-first ürün, Claude Code harness shape'ini istiyor -> **Claude Agent SDK** (Ders 17).
5. OpenAI-first ürün, handoff'lar + guardrails + tracing istiyor -> **OpenAI Agents SDK** (Ders 16).
6. Multi-agent ekip, actor-model concurrency, fault isolation -> **AutoGen v0.4** / **Microsoft Agent Framework** (Ders 14).
7. Rol-tabanlı collaboration veya event-driven deterministik workflow'lar -> **CrewAI** Crew veya Flow (Ders 15).
8. Hiçbiri değilse -> Ders 01'den doğrudan API çağrıları + stdlib loop.

Şunları üret:

- Kısa bir karar dokümanı: stack, latency hedefi, gerekli primitive'ler, gözlemlenen trade-off'lar.
- Seçilen runtime'da minimal bir iskele.
- Bugün başka bir runtime kullanılıyorsa bir migration planı.

Sert reject sebepleri:

- İş yükü request başına bir yavaş çağrı olduğunda Agno veya Mastra'yı sırf "performans" için seçmek. Performans nadiren darboğazdır.
- Bir Python monorepo'da gerekçe olmadan TypeScript runtime seçmek. Karışık-dilli agent kodu operasyonel bir vergidir.
- Stateless kısa task'lar için LangGraph seçmek. Checkpointer, basit bir workflow'un (Ders 12) kaçınacağı overhead ekler.

Refusal kuralları:

- Kullanıcı "karşılaştırmak için beş runtime'ın hepsi" isterse, reddet. İş yükünde benchmark yap; framework vendor benchmark'ları yönlendirici niteliktedir.
- Kullanıcı Mastra'nın `ee/` özelliklerini self-host etmek isterse, reddet ve lisans koşullarına yönlendir.
- Ürün uzun süreli async işe (saatler-günler) ihtiyaç duyuyorsa, self-hosted'ı reddet ve Claude Managed Agents'a veya queue-tabanlı bir mimariye (Ders 29) yönlendir.

Çıktı: karar dokümanı + iskele + README. Framework'ün üstündeki operasyonel katman için Ders 24'e (observability) ve Ders 29'a (production runtimes) işaret eden bir "sırada ne okumalı" ile bitir.
