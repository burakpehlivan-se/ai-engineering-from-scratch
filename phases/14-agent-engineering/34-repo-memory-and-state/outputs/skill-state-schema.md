---
name: state-schema
description: Agent state ve task board için proje-spesifik JSON Schema'ları, atomik write'ları olan bir Python StateManager ve schema bump'larının workbench'i bozamaması için bir migration iskelesi üret.
version: 1.0.0
phase: 14
lesson: 34
tags: [state, schema, json-schema, atomic-writes, migrations]
---

Bir repo ve içinde çalışan agent ürünü verildiğinde, workbench için schema-first state dosyaları üret.

Şunları üret:

1. Gerekli key'leri, izin verilen status değerlerini, array-vs-null disiplinini ve bir `schema_version` integer'ını kapsayan `schemas/agent_state.schema.json`.
2. Task id pattern'ini, izin verilen owner'ları, izin verilen status'ları ve acceptance array'lerini kapsayan `schemas/task_board.schema.json`.
3. Temp-and-rename atomik write'larıyla `load`, `commit` ve `update` açığa çıkaran `tools/state_manager.py`.
4. Bir sonraki schema bump'ı için `tools/migrate_state.py` iskelesi; dosya bilinmeyen bir versiyondan geliyorsa fail-loud.
5. `schema_version: 1`'de seed'lenmiş `agent_state.json` ve `task_board.json` ve taze bir backlog.

Sert reject sebepleri:

- `schema_version` field'ı olmadan schema. Migration'lar opsiyonel değildir.
- Array beklendiği yerde `null`'a izin vermek. `null`, veri gibi görünen write-time bug'ıdır.
- Düz `open(path, "w")` kullanan bir writer. Sadece atomik write'lar; kısmi dosyalar source of truth'u bozar.
- State içinde token, raw chat transcript veya PII depolamak. State repo-relevant gerçekler içindir.

Refusal kuralları:

- Repo'da version control yoksa, state dosyalarını göndermeyi reddet. Atomik write'lar artı git diff, durability hikayesidir.
- Projenin `done` transition'ını validate etmek için en az bir acceptance command'ı yoksa, `status: done` enum değerini reddet. Acceptance check'i olmadan `done` eklemek tiyatrodur.
- Proje, lock stratejisi olmadan state'i süreçler arasında paylaşmayı amaçlıyorsa, göndermeden önce o finding'i yüzeye çıkar; atomik rename gerekli ama yeterli değildir.

Çıktı yapısı:

```
<repo>/
├── agent_state.json
├── task_board.json
├── schemas/
│   ├── agent_state.schema.json
│   └── task_board.schema.json
└── tools/
    ├── state_manager.py
    └── migrate_state.py
```

Şuraya işaret eden bir "sırada ne okumalı" ile bitir:

- Ders 35, startup'ta manager'ı çağıran initialization script'i için.
- Ders 38, completion'ı skorlamak için state'i okuyan verification gate'i için.
- Ders 40, aynı schema'yı tüketen handoff generator için.
