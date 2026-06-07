---
name: workbench-audit
description: Herhangi bir agent işine başlamadan önce yedi agent workbench yüzeyini denetle ve hangilerinin eksik, kısmi veya sağlıklı olduğunu raporla.
version: 1.0.0
phase: 14
lesson: 31
tags: [workbench, audit, reliability, agent-engineering]
---

Bir repository yolu ve içinde çalışacak agent ürünü verildiğinde, yedi workbench yüzeyini denetle ve bir readiness raporu üret.

Yedi yüzey:

1. Instructions: agent'ın ilk okuduğu kök dosya (örn. `AGENTS.md`), kısa, daha derin kurallara yönlendiren.
2. State: task, dokunulan dosyalar, blocker'lar, sonraki action'ı kaydeden durable, machine-readable bir dosya.
3. Scope: her task için izin verilen dosyaları, yasak dosyaları, acceptance criteria'yı, rollback planını listeleyen bir kontrat.
4. Feedback: command, stdout, stderr, exit code'u yakalayan ve sonucu loop'a geri besleyen bir runner.
5. Verification: test, lint, type-check, smoke run çalıştıran ve acceptance criteria'yı doğrulayan bir gate.
6. Review: farklı bir rolle ikinci bir geçiş; builder kendi işini işaretleyemez.
7. Handoff: neyin değiştiğini, nedenini, neyin kaldığını ve bir sonraki en iyi action'ı özetleyen bir artifact.

Şunları üret:

- Yüzey başına bir skor: 0 eksik, 1 kısmi, 2 sağlıklı. Her skoru gözlemlediğiniz bir dosya veya süreçle ilişkilendirin.
- Kaldıraç gücüne göre sıralanmış üç öncelik: eklenirse en çok failure mode'u kaldıracak olan eksik yüzey.
- Machine-readable `workbench_audit.json` raporu artı okunabilir `workbench_audit.md` özeti.
- En zayıf yüzey için bir starter patch: skoru 0'dan 1'e taşıyan en küçük dosya değişikliği.

Sert reject sebepleri:

- Dosya yolu veya süreç referansı olmadan "sağlıklı" skorları. Kanıt olmadan denetimler çürür.
- Tek birleşik "agent config" yüzeyi. Yüzeyleri birleştirmek, bir task bozulduğunda hangisinin başarısız olduğunu gizler.
- Test'ler yavaş olduğu için verification'ı atlamak. Verification workbench'te değilse, builder'lar kendi ödevlerini işaretler.

Refusal kuralları:

- Repo'da hiç test command'ı yoksa, verification skorunu reddet ve bunu blocking finding olarak yüzeye çıkar.
- Repo'da version control history yoksa, handoff skorunu reddet ve bunu blocking finding olarak yüzeye çıkar.
- Agent ürünü root olarak veya kısıtlanmamış dosya erişimiyle çalışıyorsa, bir sandbox veya write list tanımlanana kadar scope skorunu reddet.

Çıktı yapısı:

```
workbench-audit/
├── workbench_audit.json
├── workbench_audit.md
├── patches/
│ └── <weakest-surface>.patch
└── README.md
```

Şuraya işaret eden bir "sırada ne okumalı" ile bitir:

- Ders 32, minimal repo layout için.
- Ders 33, instructions yüzeyini derinlemesine incelemek için.
- Ders 38, verification gate için.
