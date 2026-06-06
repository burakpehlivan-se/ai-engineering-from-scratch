---
name: computer-use-safety
description: Allowlist navigasyonu ve injection-marker filtrelemesi ile bir computer-use agent için adım başına safety classifier + confirmation gate üret.
version: 1.0.0
phase: 14
lesson: 21
tags: [computer-use, safety, claude, openai-cua, gemini]
---

Bir computer-use agent ve bir hedef app listesi verildiğinde, her action'ı execution'dan önce sınıflandıran bir safety katmanı üret.

Şunları üret:

1. `allow`, `reason`, `needs_confirmation` field'ları ile `SafetyClassifier.assess(action, screen) -> SafetyVerdict`.
2. Agent'ın tıklayabileceği element label'larının allowlist'i; aksi takdirde reddetme.
3. Agent'ın navigate edebileceği URL'lerin allowlist'i; listenin dışına yönlendirmelerde reddetme.
4. DOM metni, çekilen içerik ve yazılan metin üzerinde injection-marker filtresi. Herhangi bir eşleşme action'ı bloklar.
5. Hassas action'lar (login, purchase, delete, publish) için confirmation gate. Human-in-the-loop callback interface'i.
6. Trace emitter: her karar (action, verdict, reason) ile loglanır.

Sert reject sebepleri:

- Sadece ilk action üzerinde çalışan safety classifier. Her action sınıflandırılmalıdır.
- `*` formunda allowlist. Her şeye izin veren allowlist, allowlist değildir.
- Model "güvenli görünüyor" diye confirmation'ı atlamak. Confidence, safety değildir.

Refusal kuralları:

- Agent adım başına safety olmadan computer-use erişimine sahipse, gönderimi reddet.
- Agent keyfi URL'lere navigate edebiliyorsa, reddet. Allowlist veya blocklist zorunlu kıl.
- Hassas action'lar herhangi bir modda confirmation gate'ini atlıyorsa, reddet.

Çıktı: `classifier.py`, `allowlist.py`, `confirmation.py`, `trace.py`, gate policy'sini, injection marker'larını ve allowlist bakım sürecini açıklayan `README.md`. Ders 27'ye (prompt injection) ve Ders 23'e (safety kararları için OTel span attribution) işaret eden bir "sırada ne okumalı" ile bitir.
