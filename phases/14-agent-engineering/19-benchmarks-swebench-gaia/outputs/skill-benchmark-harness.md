---
name: benchmark-harness
description: FAIL_TO_PASS / PASS_TO_PASS gating, contamination check'leri ve step-count metrikleri ile bir codebase için SWE-bench şekilli bir harness üret.
version: 1.0.0
phase: 14
lesson: 19
tags: [swe-bench, gaia, agentbench, harness, evaluation]
---

Bir codebase ve bir (bug, fix) pair listesi verildiğinde, gerçek unit test'lere karşı gating yapan ve operasyonel metrikler kaydeden bir benchmark harness'i üret.

Şunları üret:

1. Task başına tanım: `(tid, description, state_before, fail_to_pass_tests, pass_to_pass_tests, solution)`.
2. Agent'ın patch'ini uygulayan, repo'nun test suite'ini bir sandbox'ta çalıştıran ve şunları kaydeden bir runner: FTP pass count, PTP pass count, step count, tokens, wall-clock, cost.
3. Bir contamination check'i: issue metnini üretilen patch'e karşı pattern-match et; >=%30 örtüşmeyi işaretle.
4. JSON olarak task başına ve toplu skorları, artı P50/P75/P95 step ve cost yayan bir reporter.
5. Her PR'da harness'i çalıştıran ve >=%5 regresyonda başarısız olan bir CI job.

Sert reject sebepleri:

- Sadece tek bir toplu sayı raporlayan harness. Task başına sonuçlar + dağılımlar zorunlu kıl.
- Sandbox olmadan test çalıştıran harness. Agent tarafından sağlanan patch'ler güvenilmeyen koddur.
- PASS_TO_PASS gate'i olmayan harness. Diğer test'leri sessizce bozan patch'ler ürünü sessizce gerilettir.

Refusal kuralları:

- Kullanıcı "sadece FAIL_TO_PASS skoru" isterse, reddet. PASS_TO_PASS ekle; mevcut test'leri kırmak, fix'i kaçırmaktan daha kötü bir regresyondur.
- Test'ler belirli bir commit'e pin'lenmemişse, reddet. Test'lerdeki drift skorları çalıştırmalar arasında karşılaştırılamaz hale getirir.
- Task'lar eğitim sırasında görülen issue metniyle örtüşüyorsa, bunu açıkça işaretle.

Çıktı: `tasks.py`, `harness.py`, `contamination.py`, `report.py`, sandbox'ı, gate'leri ve contamination policy'sini açıklayan `README.md`. Harness'in üstünde eval-driven development için Ders 30'a işaret eden bir "sırada ne okumalı" ile bitir.
