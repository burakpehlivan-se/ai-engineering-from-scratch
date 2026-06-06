---
name: runtime-shape
description: Bir production runtime shape (request-response, streaming, queue, event, cron, durable) seç ve observability'yi bağla.
version: 1.0.0
phase: 14
lesson: 29
tags: [production, runtime, queue, event, durable, observability]
---

Bir task sınıfı (beklenen süre, adım sayısı, tetikleyici tipi, latency budget'ı) verildiğinde, runtime shape'i seç.

Karar:

1. < 30s, kullanıcı bekler -> **request-response**.
2. Progressive UX veya voice -> **streaming**.
3. Dakikalar-saatler, kullanıcı beklemez -> **queue-based**.
4. Dış event'lere reaktif -> **event-driven**.
5. Periyodik housekeeping -> **cron**.
6. Yukarıdakilerden herhangi biri ve restart maliyeti yüksekse -> **durable execution** ekle.

Şunları üret:

1. Stack'inizde shape iskelesi.
2. Observability: OTel GenAI span'ları (Ders 23), bağlı backend (Ders 24).
3. Queue için: DLQ + retry policy + queue depth metric.
4. Event için: açık subscriber registry + replay path.
5. Cron için: örtüşen çalıştırmaları önlemek için lock file veya distributed lock.
6. Durable için: checkpointer backend + resume semantiği.

Sert reject sebepleri:

- 5 dakikalık bir task için senkron HTTP. Kullanıcılar telefonu kapatır; worker'lar birikir.
- DLQ olmadan queue-based. Başarısız işler kaybolur.
- Trace export olmadan background iş. Kullanıcılar şikayet edene kadar başarısızlıklar görünmez.
- "Durable state yok, sadece retry yapacağız." Uzun horizon'lar checkpoint gerektirir.

Refusal kuralları:

- Ürünün SLA + replay gereksinimleri varsa, swarm topology + non-durable runtime'ı reddet.
- Task compliance-bound ise, audit trail olmadan event-driven'ı reddet.
- Kullanıcı cron + lock yok isterse, reddet. Örtüşen cron çalıştırmaları en iyi ihtimalle duplicate work, en kötü ihtimalle veri bozulmasıdır.

Çıktı: runtime iskelesi + observability hook'ları + SLA, retry policy ve checkpointer seçimini içeren README. Ders 23'e (OTel), Ders 24'e (observability) veya hosted long-running için Ders 17'ye (Managed Agents) işaret eden bir "sırada ne okumalı" ile bitir.
