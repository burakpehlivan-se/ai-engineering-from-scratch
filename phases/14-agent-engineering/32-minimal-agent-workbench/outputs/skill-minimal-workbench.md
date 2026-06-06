---
name: minimal-workbench
description: Herhangi bir repo için üç-dosyalık minimum viable agent workbench'i kur — kısa AGENTS.md router'ı, durable agent_state.json ve projenin mevcut backlog'una anahtarlı bir JSON task_board.json.
version: 1.0.0
phase: 14
lesson: 32
tags: [workbench, agents-md, state, task-board, scaffold]
---

Bir repo yolu ve kısa bir backlog verildiğinde, minimum viable agent workbench'i iskele.

Şunları üret:

1. 80 satırı aşmayan `AGENTS.md`. Şuraya yönlendirmeli: state dosyası, task board, daha derin rules dokümanı (boş olsa bile) ve verification command. Bu dosyada prose tutorial yok.
2. Şu key'lerle `agent_state.json`: `active_task_id`, `touched_files`, `assumptions`, `blockers`, `next_action`. Tüm opsiyonel field'lar default olarak boş array veya boş string, array'ler için asla `null` değil.
3. Bir JSON task array'i olarak `task_board.json`. Her task `id`, `goal`, `owner` (`builder` | `reviewer` | `human`), `acceptance` (string listesi) ve `status` (`todo` | `in_progress` | `done` | `blocked`) içerir.
4. Yüzey başına tek bir H2 ile `docs/agent-rules.md` placeholder'ı, böylece sonraki dersler onu doldurabilir.

Sert reject sebepleri:

- 80 satırı aşan veya 10 satırın altında `AGENTS.md`. Çok uzun, agent atlar; çok kısa, hiçbir routing taşımaz.
- Chat history'e referans veren state dosyası, repo'ya değil. Repo, system of record'dur.
- `acceptance` olmadan task board. Acceptance criteria olmayan task'ler "iyi görünüyor" rubber stamp'larına dönüşür.
- `owner`'ı `agent` veya `model` olan task'lar. Owner'lar entity değil, roldür.

Refusal kuralları:

- Repo'da verification command yoksa, bir tane sağlanana veya stub'lanana kadar `AGENTS.md` yazmayı reddet. Eksik bir gate'e işaret eden router, router olmamasından daha kötüdür.
- Backlog 12'den fazla açık task içeriyorsa, reddet ve kullanıcıdan bölmesini iste. Bir ekranı aşan board'lar planning theater'a kayar.
- Proje tracked dosyalarda secret'lar ile geliyorsa, state dosyasını yazmayı reddet ve secret sızıntısını önce blocking finding olarak yüzeye çıkar.

Çıktı yapısı:

```
<repo>/
├── AGENTS.md
├── agent_state.json
├── task_board.json
└── docs/
    └── agent-rules.md
```

Şuraya işaret eden bir "sırada ne okumalı" ile bitir:

- Ders 33, rules placeholder'ını executable constraint'lere dönüştürmek için.
- Ders 34, durable state schema'sı için.
- Ders 36, task başına scope kontratı için.
