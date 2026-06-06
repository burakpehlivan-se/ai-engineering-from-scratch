---
name: state-graph
description: Tipli state, conditional edge'ler, node başına checkpointing ve durable resume içeren LangGraph şekilli bir state machine üret.
version: 1.0.0
phase: 14
lesson: 13
tags: [langgraph, state-machine, durable, checkpointing, human-in-the-loop]
---

Bir hedef runtime, bir state shape'i, bir node fonksiyonu seti ve bir checkpointer backend'i verildiğinde, stateful bir agent graph'ı üret.

Şunları üret:

1. Tipli bir `State` (dict veya Pydantic). Her field'ı belgele. Node'lar state'i okur; update dönerler.
2. `add_node`, `add_edge`, `add_conditional_edges`, `set_entry` artı `START`/`END` sentinelleri ile bir `StateGraph`.
3. `save(session_id, node, state)` ve `load_latest(session_id)` ile bir `Checkpointer` interface'i. Default olarak SQLite; Postgres/Redis/custom'a izin ver.
4. Graph'ta ilerleyen, her node'dan sonra state'i serialize eden, human-in-the-loop için `PausedAtNode`'u yakalayan ve opsiyonel `state_override` ile `resume_from`'ı destekleyen bir `Runner`.
5. Üç topology helper'ı: supervisor (central router), swarm (shared-tool handoffs), hierarchical (subgraph'ler).

Sert reject sebepleri:

- Açık random-seed veya wall-clock capture olmadan deterministik olmayan node'lar. Resume, input state verildiğinde node çıktısının reproducible olduğunu varsayar.
- Sadece "summary" state'i kaydeden bir checkpointer. Tam state'i serialize et; yoksa resume bozulur.
- Her edge'in conditional olduğu graph'lar. Ara sıra branch veren lineer chain'leri tercih et.

Refusal kuralları:

- Kullanıcı persistence olmadan bir state graph isterse, reddet. Bütün mesele durable resume; resume'a ihtiyacın yoksa Ders 12'deki workflow pattern'lerini kullan.
- Kullanıcı "sadece başarıda checkpoint at" isterse, reddet. Başarısızlıkların da state'e ihtiyacı var — debugging orada başlar.
- Graph ~30 node'dan fazlaysa, flat layout'u reddet ve nested subgraph'leri zorunlu kıl. 30 node'luk flat graph'lar review edilemez.

Çıktı: `state.py`, `graph.py`, `checkpointer.py`, `runner.py`, state schema'sını, checkpointer seçimini ve resume semantiğini açıklayan `README.md`. Actor-model alternatifi için Ders 14'e, handoffs/guardrails katmanı için Ders 16'ya veya graph adımlarında OTel span'ları için Ders 23'e işaret eden bir "sırada ne okumalı" ile bitir.
