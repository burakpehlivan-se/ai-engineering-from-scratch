---
name: init-script
description: Bir projeyi sorgula ve beş probe ile deterministik bir init_agent.py artı herhangi bir probe başarısız olursa agent'ı başlatmayı reddeden bir CI workflow'u yay.
version: 1.0.0
phase: 14
lesson: 35
tags: [init, probes, ci, workbench, fail-loud]
---

Bir repo, agent ürünü ve onun dependency yüzeyi verildiğinde, proje-spesifik bir init script'i ve CI bağlantısı üret.

Şunları üret:

1. Şu probe'larla `tools/init_agent.py`: runtime versiyonu, listelenen dependency'ler, test command çözümlenebilirliği, gerekli env var'lar, state dosyası freshness'i.
2. Script'in yanında belgelenen `init_report.json` schema'sı. Her probe `(name, status: pass|warn|fail, detail)` döner.
3. Script'i çalıştıran ve herhangi bir fail-severity probe'unda agent job'ını bloklayan `.github/workflows/agent-init.yml` (veya eşdeğeri).
4. Agent runtime'ın her session başlamadan önce çağırabileceği bir `pre-task` hook script'i.
5. `docs/init.md` içinde her probe'u, severity'sini ve bir başarısızlığın nasıl düzeltileceğini listeleyen dokümantasyon.

Sert reject sebepleri:

- Timeout olmadan ağa çağrı yapan probe'lar. Init hızlı ve offline-safe olmalıdır.
- LLM çağrıları gerektiren probe'lar. Init deterministik plumbing'dir.
- Wrapper'ın yuttuğu sıfır-olmayan exit code. Fail loud bütün mesele.
- İdempotent olmadan state'e dokunan probe'lar. Art arda iki çalıştırma, timestamp dışında özdeş raporlar üretmelidir.

Refusal kuralları:

- Projenin test command'ı yoksa, script'i göndermeyi reddet. Bunun yerine boşluğu workbench denetimine ekle.
- Env var listesi script'in yazdıracağı secret'lar içeriyorsa, reddet ve redaction'ı zorla. Init raporları asla secret taşımamalıdır.
- Bir probe dry run'da üç saniyeden uzun sürüyorsa, göndermeden önce timing finding'ini yüzeye çıkar. Uzun probe'lar init'i seromoniye çevirir.

Çıktı yapısı:

```
<repo>/
├── tools/
│ ├── init_agent.py
│ └── pre_task.sh
├── docs/
│ └── init.md
└── .github/
 └── workflows/
 └── agent-init.yml
```

Şuraya işaret eden bir "sırada ne okumalı" ile bitir:

- Ders 36, init report'un `repo_paths`'ini kullanan task başına scope kontratı için.
- Ders 37, çözümlenmiş test command'ını tüketen runtime feedback loop'u için.
- Ders 38, probe'ların geçmesine bağlı olan verification gate'i için.
