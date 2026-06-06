---
name: task-store-designer
description: Uzun süre çalışan bir MCP tool'u için task store'u tasarla: state shape, ttl, durability, cancellation, crash recovery.
version: 1.0.0
phase: 13
lesson: 13
tags: [mcp, tasks, durable-store, long-running, sep-1686]
---

Uzun süre çalışan bir tool verildiğinde (araştırma, build, export, rapor üretimi), SEP-1686 task augmentation'ı destekleyen task store'u tasarla.

Şunları üret:

1. State shape. Minimum alanlar: `id`, `state`, `progress`, `result`, `error`, `ttl`, `created_at`. Opsiyonel: `request_meta`, `parent_task_id` (gelecekteki subtask'lar için).
2. Durability seçimi. Oyuncak için filesystem; tek process için SQLite; çoklu replica için Redis. Gerekçelendir.
3. taskSupport bayrağı. Tool başına `forbidden`, `optional` veya `required`; tek satırlık gerekçe.
4. Cancellation planı. Worker'ın bir cancel sinyalini nasıl kontrol ettiği; kısmi progress'te ne olduğu.
5. Crash recovery. Boot-time reload kuralı; `CRASH_RECOVERY` başarısızlıklarının client'a nasıl göründüğü.

Sert reject sebepleri:
- Tamamlanmış sonuçları ttl içinde kaybeden herhangi bir store.
- Açık terminal state'leri (`completed`, `failed`, `cancelled`) olmayan herhangi bir task state'i.
- Idempotent olmayan herhangi bir cancellation.

Refusal kuralları:
- Tool 5 saniyenin altında çalışıyorsa, task'a terfi ettirmeyi reddet. Senkron daha basittir.
- Task 10 MB'tan fazla sonuç üretecekse, reddet ve streaming content block'ları öner.
- Server, state'i kalıcılaştırabilen bir process'e sahip değilse (stateless edge function), reddet ve dayanıklı bir runtime'a taşınmayı öner.

Çıktı: state shape, durability seçimi, taskSupport bayrağı, cancellation planı ve crash-recovery kuralını içeren tek sayfalık bir store tasarımı. SEP-1686 subtask'ları yayımlandığında bu tasarımı etkileyip etkilemeyeceğine dair tek satırlık bir öneriyle bitir.
