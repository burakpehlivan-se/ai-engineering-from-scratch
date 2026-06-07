---
name: handoff-generator
description: Workbench artifact'larından session sonu handoff paketleri üret, hem okunabilir Markdown hem de yedi kanonik field'a anahtarlanmış machine-readable JSON üret.
version: 1.0.0
phase: 14
lesson: 40
tags: [handoff, generator, session-end, packet, next-action]
---

Bir workbench (state, verdict, review, feedback log, diff) verildiğinde, agent runtime'a bağlı bir session-sonu handoff generator'ı üret.

Şunları üret:

1. `generate_handoff(snapshot) -> (markdown, payload)` açığa çıkaran `tools/generate_handoff.py`.
2. `outputs/handoff/<session_id>/handoff.md` ve `handoff.json`.
3. Yedi gerekli field'ı ve feedback tail format'ını kapsayan `handoff.schema.json`.
4. Generator'ı çalıştıran ve herhangi bir field eksikse session'ı kapatmayı reddeden session-end hook script'i.
5. Yedi field'ı, kaynaklarını ve trimming policy'sini listeleyen `docs/handoff.md`.

Sert reject sebepleri:

- `next_action` olmadan handoff. Handoff kılığında status raporları bir sonraki session'ı zehirler.
- Özeti elle yazan generator. Agent'ın işi workbench'i generatable bir state'te bırakmaktır.
- JSON'dan ayrılan markdown paket. JSON source'dur; markdown JSON'un bir render'ıdır.
- 30 entry'den uzun feedback tail. Tam log version control'dedir; paket küçük kalmalıdır.

Refusal kuralları:

- Verification raporu eksikse, paketi üretmeyi reddet. Verdictsiz handoff bir dilektir.
- Review raporu eksikse ve bir insan reviewer bekleniyorsa, reddet ve önce review pass'ını zorunlu kıl.
- Diff özeti boşsa ama session 5 dakikadan uzun sürdüyse, üretmeden önce anomaliliği yüzeye çıkar; gerçek bir no-op'tan çok takılmış bir session'dan şüphelen.

Çıktı yapısı:

```
<repo>/
├── outputs/handoff/<session_id>/
│ ├── handoff.md
│ └── handoff.json
├── tools/generate_handoff.py
├── handoff.schema.json
└── docs/handoff.md
```

Şuraya işaret eden bir "sırada ne okumalı" ile bitir:

- Ders 41, real-style bir örnek app üzerinde end-to-end exercise için.
- Ders 42, generator'ı capstone workbench pack'ine paketlemek için.
- Ders 29 (Production Runtimes), session-end'i queue, event ve cron tetikleyicilerine bağlamak için.
