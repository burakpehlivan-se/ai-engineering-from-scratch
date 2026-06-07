---
name: rule-set-builder
description: Bir proje sahibiyle röportaj yap, mevcut prose instructions'larını beş operasyonel kategoriye sınıflandır ve versiyonlanmış bir agent-rules.md artı bir Python checker stub'ı yay.
version: 1.0.0
phase: 14
lesson: 33
tags: [rules, instructions, constraints, checker, workbench]
---

Bir repo ve herhangi bir mevcut prose instructions verildiğinde (`AGENTS.md`, `CONTRIBUTING.md`, onboarding docs), workbench'in execute edebileceği beş kategorili bir rule set'i üret.

Beş kategori:

1. `startup` — iş başlamadan önce ne doğru olmalı.
2. `forbidden` — ne asla olmamalı.
3. `definition_of_done` — task'ın tamamlandığını ne kanıtlar.
4. `uncertainty` — emin olmadığında agent ne yapar.
5. `approval` — ne insan onayı gerektirir.

Şunları üret:

1. Kural başına bir `##` heading ile `docs/agent-rules.md`. Her kural `category`, `check` ve tek satırlık bir açıklama taşır.
2. `check` başına bir method açığa çıkaran `RuleChecker` class'ı ile `tools/rule_checker.py`. Her method bir `TurnTrace` dataclass'ı alır ve `bool` döner.
3. Kuralları yükleyen, checker'ı bir trace üzerinde çalıştıran ve bir `rule_report.json` yayan `tools/rule_report.py` runner'ı.
4. Bir migration notes dosyası: hangi prose satırları hangi kurala dönüştü, hangileri aspirasyonel olarak düşürüldü, neden.

Sert reject sebepleri:

- `check` field'ı olmayan kurallar. Yalnızca aspirasyonel kurallar onboarding docs'a aittir, workbench rule set'ine değil.
- Tek bir "dikkatli ol" kuralı. Bir kategori ve bir check belirt veya kaldır.
- LLM çağrıları gerektiren check'ler. Rule check'leri deterministik ve ucuz olmalıdır, böylece her turn'de çalışabilir.
- 200 satırı aşan rule dosyaları. Kategoriye göre `agent-rules.{startup,forbidden,done,uncertainty,approval}.md` olarak böl ve bir parent index'ten yönlendir.

Refusal kuralları:

- Agent ürünü bir `TurnTrace` sağlayamıyorsa (instrumentation yok), en azından `read_state_file`, `edited_files` ve `tests_exit_code` kaydedilene kadar checker'ı bağlamayı reddet.
- Mevcut instructions çoğunlukla aspirasyonel ise (>%50), kuralları yaymadan önce o finding'i yüzeye çıkar. Rule set'i ince görünecek; bu doğrudur.
- Geçmiş tek bir olay nedeniyle bir kural ekleniyorsa, gelecekteki incelemenin hâlâ gerekli olup olmadığına karar verebilmesi için olay id'sini ekle.

Çıktı yapısı:

```
<repo>/
├── docs/
│ └── agent-rules.md
├── tools/
│ ├── rule_checker.py
│ └── rule_report.py
└── docs/migration-notes.md
```

Şuraya işaret eden bir "sırada ne okumalı" ile bitir:

- Ders 36, forbidden kategorisini genişleten task başına scope kontratları için.
- Ders 38, rule report'u tüketen verification gate'leri için.
- Ders 39, rule compliance'ı skorlayan reviewer agent için.
