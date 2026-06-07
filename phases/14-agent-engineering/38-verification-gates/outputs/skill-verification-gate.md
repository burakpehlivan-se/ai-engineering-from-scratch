---
name: verification-gate
description: Scope, rule ve feedback artifact'larını task başına tek bir verification_report.json'da birleştiren deterministik bir verification gate'i, artı yeşil bir verdict olmadan merge'ı reddeden CI bağlantısı üret.
version: 1.0.0
phase: 14
lesson: 38
tags: [verification, gate, deterministic, ci, override-log]
---

Bir projenin acceptance criteria'sı ve mevcut workbench artifact'ları verildiğinde, verification gate'ini ve override audit log'unu üret.

Şunları üret:

1. `verify(task_id, artifacts) -> VerdictReport` açığa çıkaran `tools/verify_agent.py`. Saf fonksiyon, deterministik, LLM çağrısı yok.
2. Tek source of truth verdict olarak `outputs/verification/<task_id>.json`.
3. İmzalı override entry'lerini `outputs/verification/overrides.jsonl`'e append eden `tools/override.py` (reason, user id, timestamp, finding code içermeli).
4. `passed: false` üzerinde başarısız olan ve raporu inline yüzeye çıkaran CI workflow'u.
5. Her check'i, severity'sini, source artifact'ını ve override policy'sini listeleyen `docs/verification.md`.

Sert reject sebepleri:

- LLM çağıran bir check. Gate deterministik plumbing'dir; LLM yargısı reviewer'a aittir.
- Agent'ın imzalı bir entry olmadan alabileceği bir override yolu. Override'lar yalnızca insan içindir.
- Tüketilen artifact path'lerini atlayan bir verification raporu. Raporlar denetlenebilir olmalıdır.
- Workflow'un sessizce downgrad edebileceği block-severity finding'ler. Severity, read time'da değil write time'da sabitlenir.

Refusal kuralları:

- Projenin acceptance command'ı yoksa, bir tane var olana kadar gate'i göndermeyi reddet. Hiçbir şey kanıtlamayan gate tiyatrodur.
- Rule report yoksa, rule check'ini atlamayı reddet; fail closed.
- Feedback log yoksa, acceptance check'ini atlamayı reddet; eksik log'lar kendi başlarına bir block'tur.
- Override entry'leri version-controlled değilse, override yolunu bağlamayı reddet; kayıt dışı override'lar gate'i boşa çıkarır.

Çıktı yapısı:

```
<repo>/
├── tools/
│ ├── verify_agent.py
│ └── override.py
├── outputs/verification/
│ ├── overrides.jsonl
│ └── <task_id>.json
├── docs/verification.md
└── .github/workflows/verify.yml
```

Şuraya işaret eden bir "sırada ne okumalı" ile bitir:

- Ders 39, yeşil bir verdict'ten sonra devreye giren reviewer agent için.
- Ders 40, verdict'i pakete dahil eden handoff generator için.
- Ders 41, real-style bir örnek app'a karşı gate'i çalıştırmak için.
