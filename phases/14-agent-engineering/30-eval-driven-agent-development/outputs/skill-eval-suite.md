---
name: eval-suite
description: Evaluator-optimizer loop ve CI gate'leri ile üç katmanlı bir eval suite (static benchmarks, custom offline, online production) üret.
version: 1.0.0
phase: 14
lesson: 30
tags: [evaluation, ci, regression, benchmarks, llm-judge]
---

Bir agent ürünü verildiğinde, CI'a bağlı üç katmanlı bir eval suite üret.

Şunları üret:

1. **Static benchmark katmanı** — en az bir ilgili benchmark (kod için SWE-bench Verified, tool use için BFCL V4, web için WebArena, desktop için OSWorld, generalist için GAIA). Her zaman +-denetlenen skoru yanında raporla.
2. **Custom offline katmanı** — domain-spesifik boyutlarda (factual, tone, scope, refusal quality) puanlanan en az bir LLM-judge rubric'i. Agent çalıştıktan sonra gerçek state'i sorgulayan en az bir execution-based case. Gold path'li en az bir trajectory-based case.
3. **Online eval katmanı** — session replay'leri, guardrail-tetiklenen alert'ler, OTel GenAI span'ları (Ders 23) üzerinden adım başına cost/latency takibi.
4. **Evaluator-optimizer runner** — agent'ı round cap ile propose / judge / refine içine sar.
5. **CI gate** — baseline'a göre >=%5 regresyonda build'i başarısız kıl. Baseline'ı zaman içinde takip et.
6. **Case mapping** — Phase 14 derslerindeki her guardrail ve her learned rule'ın en az bir case'i var.

Sert reject sebepleri:

- Baseline'ı olmayan eval suite. Referans olmadan regresyonu tespit edemezsin.
- Factual task'larda harici grounding olmadan LLM-judge. CRITIC pattern (Ders 05) zorunludur.
- Pin'lenmiş seed'leri veya snapshot state olmadan flaky case'ler. False alarm'lar ekibin eval'lere olan güvenini aşındırır.

Refusal kuralları:

- Kullanıcı "sadece happy path" isterse, reddet. Her failure mode'un (Ders 26) bir case'i olmalıdır.
- Kullanıcı "CI gate yok" isterse, ücretli kullanıcılara dokunan ürünler için reddet. Eval drift aksi takdirde görünmez.
- Kullanıcı "tüm LLM-judge'lar" isterse, factual ve compliance task'larında reddet. Orada execution-based veya programmatic evaluator'lar zorunludur.

Çıktı: `cases/benchmarks/`, `cases/custom/`, `cases/online/`, `runner.py`, `ci_gate.py`, rubric'leri, baseline'ları ve Phase 14 mapping tablosunu açıklayan `README.md`. Ders 24'e (observability), Ders 26'ya (failure modes) veya substrate için Ders 23'e (OTel) işaret eden bir "sırada ne okumalı" ile bitir.
