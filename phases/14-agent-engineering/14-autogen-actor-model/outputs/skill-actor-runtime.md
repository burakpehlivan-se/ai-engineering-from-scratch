---
name: actor-runtime
description: Private state, inbox-per-actor, yalnızca message-tabanlı IPC, fault isolation ve dead-letter queue ile AutoGen v0.4 şekilli bir actor runtime üret.
version: 1.0.0
phase: 14
lesson: 14
tags: [autogen, actor-model, messaging, fault-isolation, dead-letter]
---

Çoklu agent'lı bir task verildiğinde, bir actor runtime ve gereken agent actor'larını üret.

Şunları üret:

1. `sender`, `recipient`, `topic`, `body`, `mid` ile `Message` tipi.
2. `receive(message, runtime)` ile `Actor` base class'ı. Actor state'i private'dır.
3. Paylaşılan bir queue, `send()`, `run_until_idle()` ve bir dead-letter queue ile `Runtime`. Handler'lardaki exception'lar DLQ'ya gider; propagate etme.
4. Bir topology helper'ı: RoundRobin (sabit rotasyon), Selector (LLM sıradakini seçer) veya custom broadcast.
5. Mesaj başına observability hook'ları: Ders 23'e göre `gen_ai.agent.name` ve `gen_ai.operation.name` ile OTel span'ları yay.

Sert reject sebepleri:

- Recipient döndürene kadar sender'ı bloklayan senkron message passing. Bu v0.2 modelidir; fault isolation'ı kırar.
- Actor'ler arasında paylaşılan mutable state. Actor'lar state'i mesajlarla veya hiç okumaz.
- Handler exception'larını propagate eden bir runtime. Başarısızlıklar DLQ'ya aittir; diğer actor'lar çalışmaya devam etsin.

Refusal kuralları:

- Task'ta sadece sabit bir ping-pong ile iki actor varsa, actor çerçevesini reddet ve prompt chain (Ders 12) öner. Actor'lar maliyeti >=3 actor veya async concurrency olduğunda hak eder.
- Kullanıcı "daha kolay debugging için senkron mod" isterse, reddet. Bunun yerine logging + tracing (Ders 23) öner.
- Domain kesinlikle tek bir specialist ile request/response ise, actor ekibi yerine routing (Ders 12) öner.

Çıktı: `message.py`, `actor.py`, `runtime.py`, `teams.py`, DLQ policy'sini, topology seçimini ve OTel span'larının nasıl bağlandığını açıklayan `README.md`. Actor'lar müzakere ediyorsa Ders 25'e (multi-agent debate), tracing gerekliyse Ders 23'e (OTel) veya ileriye dönük runtime istiyorsan Microsoft Agent Framework'e işaret eden bir "sırada ne okumalı" ile bitir.
