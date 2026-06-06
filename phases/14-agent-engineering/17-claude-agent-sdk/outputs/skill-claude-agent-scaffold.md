---
name: claude-agent-scaffold
description: Subagent'lar, lifecycle hook'ları, session store, MCP server attachment'ı ve W3C trace propagation ile bir Claude Agent SDK app'i iskele.
version: 1.0.0
phase: 14
lesson: 17
tags: [claude-agent-sdk, subagents, hooks, session-store, mcp]
---

Bir ürün domain'i ve bir MCP server listesi verildiğinde, bir Claude Agent SDK app'i iskele.

Şunları üret:

1. Instructions, built-in tool erişimi (read_file, write_file, shell, grep, glob, web fetch) ve custom function tool'ları ile ana bir agent tanımı.
2. Parallelization ve context isolation için subagent spawner. Orchestrator context bütçesini aksi takdirde patlatacağı zaman kullan.
3. Register edilmiş lifecycle hook'ları: audit için PreToolUse + PostToolUse, setup için SessionStart, teardown için SessionEnd, kural zorlaması için UserPromptSubmit (pro-workflow pattern'lerine bak).
4. `list_subkeys`'i bir subagent ağacı oluşturmak üzere bağlanmış session store (default SQLite).
5. Dış tool/resource yüzeyleri için MCP server attachment'ı.
6. Caller'dan gelen OTel span'larının CLI boyunca devam etmesi için W3C trace context propagation.

Sert reject severepleri:

- Tek-tool'luk bir task için subagent spawn etmek. Subagent'lar parallelization veya context isolation içindir; "tek bir read_file çağrısı" için değil.
- Senkron pahalı iş yapan hook'lar. Hook'lar mikrosaniye-milisaniye aralığında olmalıdır. Uzun iş bir subagent'a aittir.
- Cascade-delete policy'si olmayan session store'ları. Orphaned subagent session'ları storage'ı şişirir.

Refusal kuralları:

- Ürün uzun süreli async işe (saatler-günler) ihtiyaç duyuyorsa, self-hosted SDK'yı reddet ve Claude Managed Agents'a yönlendir.
- Kullanıcı paylaşılan bir konuma `--session-mirror` isterse, reddet. Session transcript'leri PII taşır; kullanıcı başına şifreli storage'a mirror'la.
- Agent, tool use olmadan UX için raw LLM streaming'e bağlıysa, Agent SDK'yı reddet ve doğrudan Client SDK'yı öner.

Çıktı: `agent.py`, `tools.py`, `hooks.py`, `session.py`, subagent policy'sini, hook registry'sini, session backend'ini, MCP attachment'larını ve OTel bağlantısını açıklayan `README.md`. Voice handoff'ları için Ders 22'ye, OTel span attribution'ı için Ders 23'e veya ürün production runtime shape'ine ihtiyaç duyuyorsa Ders 18'e işaret eden bir "sırada ne okumalı" ile bitir.
