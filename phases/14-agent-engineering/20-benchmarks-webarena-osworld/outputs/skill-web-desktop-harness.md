---
name: web-desktop-harness
description: Execution-based evaluation ve trajectory-efficiency metrikleri ile WebArena/OSWorld şekilli bir harness üret.
version: 1.0.0
phase: 14
lesson: 20
tags: [webarena, osworld, harness, trajectory-efficiency]
---

Bir hedef app (web veya desktop) ve gold trajectory'li bir task listesi verildiğinde, bir eval harness'i üret.

Şunları üret:

1. Task tanımları: `(tid, description, gold_steps, success_predicate, state_reset)`.
2. Runner: agent'ı çalıştırır, her action'ı yakalar, step count + elapsed time + success state'i kaydeder.
3. Trajectory-efficiency metriği: `agent_steps / gold_steps`. Task başına ve toplu raporla.
4. Task'lar arasında state reset — bir task'ı asla başka birinin kirlettiği state üzerinde çalıştırma.
5. Failure-mode classifier'ı: her başarısızlık için, bir grounding miss (yanlış element) mi yoksa planning miss (yanlış action) mı olduğunu etiketle.

Sert reject sebepleri:

- Task'lar arasında state reset olmaması. Task'lar arası contamination tüm skorları geçersiz kılar.
- Sadece success-rate raporlaması. Trajectory efficiency 2026 standardıdır.
- DOM parity olmadan yalnızca screenshot kullanan harness. Bazı agent'lar DOM+vision kullanır; yüzeyi özellikle kısıtlamadıkça ikisini de ver.

Refusal kuralları:

- Task'ların gold trajectory'leri yoksa, reddet. Efficiency'yi onlar olmadan ölçemezsin.
- App belirli bir versiyona pin'lenmemişse, reddet. Drift, çalıştırmalar arası karşılaştırmaları geçersiz kılar.
- Agent'ın yıkıcı tool'ları (delete, publish) varsa, app'in bir sandbox kopyasını zorunlu kıl.

Çıktı: `tasks.py`, `runner.py`, `failure_classifier.py`, `report.py`, reset policy'sini, gold-trajectory kaynağını ve grounding-vs-planning ayrımını açıklayan `README.md`. Ders 21'e (computer use modelleri) veya Ders 30'a (eval-driven development) işaret eden bir "sırada ne okumalı" ile bitir.
