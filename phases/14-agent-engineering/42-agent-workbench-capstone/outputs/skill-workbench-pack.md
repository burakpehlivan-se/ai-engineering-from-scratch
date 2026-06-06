---
name: workbench-pack
description: Projeye göre ayarlanmış, takımın geçmişine göre bilenmiş kurallar, repo'ya eşleştirilmiş scope glob'ları ve bir domain-spesifik entry ile genişletilmiş rubric boyutlarıyla drop-in bir agent workbench pack üret.
version: 1.0.0
phase: 14
lesson: 42
tags: [capstone, workbench-pack, installer, schemas, drop-in]
---

Bir repo, takımın incident geçmişi ve içinde çalışan agent ürünü verildiğinde, ayarlanmış bir agent-workbench-pack ve bir installer yay.

Şunları üret:

1. Kanonik layout ile eşleşen `agent-workbench-pack/` dizini: AGENTS.md, docs/, schemas/, scripts/, bin/, README.md, VERSION.
2. `--force` olmadan mevcut bir pack'i ezberletmeyi reddeden ve `.workbench-version`'ı hedef repo'ya yazan `bin/install.sh`.
3. `agent-rules.md`'nin proje-ayarlı versiyonları (takımın son altı incident'ından türetilmiş kategori başına en az bir kural ile), `reviewer-rubric.md` (altıncı bir domain boyutu ile) ve `scope_contract.schema.json` (proje-spesifik glob'lar ile).
4. Script'ler ile schema'lar arasında veya VERSION ile schema'ların `schema_version`'ı arasındaki drift'te başarısız olan bir `lint_pack.py` script'i.
5. Demo branch'lerinde pack'i yükleyen ve bilinen-iyi bir task'a karşı verification gate'ini çalıştıran opsiyonel CI entegrasyonu.

Sert reject sebepleri:

- Proje-spesifik task'lar içeren bir pack. Task'lar hedef repo'nun board'unda yaşar.
- Tek bir vendor SDK'sına bağlı bir pack. Sadece framework-agnostic; SDK bağlantısı hedef repo'nun işidir.
- State dosyalarını mutate eden bir installer. Installer idempotent surface-only'dir; state agent'a ve insanlara aittir.
- Karşılık gelen check fonksiyonu olmayan kurallar. Aspirasyonel kurallar onboarding'e aittir, pack'e değil.

Refusal kuralları:

- Incident geçmişi boşsa, ayarlanmış `agent-rules.md` göndermeyi reddet. Kanonik default'u kullan ve boşluğu yüzeye çıkar.
- Hedef repo'nun CI'ı install ile uyumsuzsa (`.github/workflows/` yok, eşdeğeri yok), opsiyonel CI step'ini reddet ve manual yolu belgele.
- Takım pack'in private fork'unu kullanıyorsa, public bir installer yazmayı reddet. Private installer'lar private invariant'lar taşır.

Çıktı yapısı:

```
agent-workbench-pack/
├── AGENTS.md
├── docs/
├── schemas/
├── scripts/
├── bin/install.sh
├── lint_pack.py
├── VERSION
└── README.md
```

Şuraya işaret eden bir "sırada ne okumalı" ile bitir:

- Ders 41, bu pack'in iyileştirdiği before/after benchmark için.
- Ders 30 (Eval-Driven Agent Development), pack'in verdict'larını tüketen eval loop'u için.
- [SkillKit](https://github.com/rohitg00/skillkit), pack'i 32 AI agent'a dağıtmak için.
