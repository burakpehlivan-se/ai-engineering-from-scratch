---
name: workbench-benchmark
description: Aynı task'ı projenin kendi sample app'inde prompt-only ve workbench-guided pipeline'lardan geçir ve beş-outcome'lı bir before/after raporu yay.
version: 1.0.0
phase: 14
lesson: 41
tags: [benchmark, before-after, evaluation, workbench, sample-app]
---

Bir repo, bir agent ürünü ve küçük bir sample app verildiğinde, prompt-only ve workbench-guided pipeline'ları karşılaştıran portable bir evaluation harness'i üret.

Şunları üret:

1. `eval/sample_app/` — projenin domain'inden çekilmiş minimum-viable bir sample app.
2. Bir task açıklaması alan ve bir `TaskOutcome` döndüren `eval/run_prompt_only.py` ve `eval/run_workbench.py`.
3. Her iki pipeline'ı çalıştıran ve `before-after-report.md` artı `comparison.json` yazan `eval/report.py`.
4. Sabit bir task suite'inde workbench outcome'ları gerilediğinde başarısız olan CI workflow'u.
5. Beş outcome'u ve neyin regresyon sayıldığını açıklayan `docs/benchmark.md`.

Sert reject sebepleri:

- Sadece bir pipeline ile benchmark. Karşılaştırma bütün mesele.
- Payda olmadan yüzde olarak ifade edilen outcome'lar. Her zaman `n / m` raporla.
- Agent ürününün eğitildiği sample app. Domain-tuned bir fixture kullan.
- False negative'leri gizleyen raporlar. Prompt-only'nin daha hızlı olduğu task'lar numaralandırılmalıdır.

Refusal kuralları:

- Projenin acceptance command'ı yoksa, benchmark'ı göndermeyi reddet. Ölçülecek bir şey yok.
- Workbench pipeline medyan task'ta prompt-only pipeline'dan 3x'ten fazla sürüyorsa, o finding'i yüzeye çıkar; workbench'in modele değil sadeleştirmeye ihtiyacı var.
- Harness offline çalıştırılamıyorsa, CI'a bağlamayı reddet. Ağ flakiness karşılaştırmayı bozacaktır.

Çıktı yapısı:

```
<repo>/
├── eval/
│ ├── sample_app/
│ ├── run_prompt_only.py
│ ├── run_workbench.py
│ └── report.py
├── outputs/eval/
│ ├── before-after-report.md
│ └── comparison.json
├── docs/benchmark.md
└── .github/workflows/benchmark.yml
```

Şuraya işaret eden bir "sırada ne okumalı" ile bitir:

- Ders 42, workbench pipeline'ının kullandığı her yüzeyi birleştiren capstone pack için.
- Ders 19 (SWE-bench, GAIA, AgentBench), bunun tamamladığı makro benchmark'lar için.
- Ders 30 (Eval-Driven Agent Development), benchmark bağlandıktan sonra devam eden eval loop'ları için.
