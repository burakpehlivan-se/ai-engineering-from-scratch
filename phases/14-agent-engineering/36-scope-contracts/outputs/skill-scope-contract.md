---
name: scope-contract
description: Allowed/forbidden glob'ları, acceptance criteria ve rollback planı ile task başına scope kontratları, artı her agent diff'te çalışan CI-ready glob-aware bir checker üret.
version: 1.0.0
phase: 14
lesson: 36
tags: [scope, contract, globs, diff-check, ci]
---

Bir task açıklaması ve bir repo layout'u verildiğinde, bir scope kontratı ve diff-aware bir checker üret.

Şunları üret:

1. Şu field'larla task için `scope_contract.json`: `task_id`, `goal`, `allowed_files` (glob'lar), `forbidden_files` (glob'lar), `acceptance_criteria`, `rollback_plan`, `approvals_required`.
2. Bir kontrat yolu ve bir dokunulan dosya listesi alan ve herhangi bir ihlalde sıfır-olmayan exit ile birlikte bir `ScopeReport` döndüren `tools/scope_check.py`.
3. Checker'ı merge diff'ine karşı çalıştıran CI step'i (`.github/workflows/scope-check.yml` veya eşdeğeri).
4. Kontratların change history ile birlikte gelmesi için `outputs/scope/closed/<task_id>.json` arşivleme kuralı.

Sert reject sebepleri:

- `forbidden_files` olmadan kontrat. Negatif alan kontratın parçasıdır.
- Kod dizinleri için raw path yerine glob listeyen kontrat. Refactor'lar raw path'leri bir gecede geçersiz kılar.
- Boş veya "runbook'a bak" olan `rollback_plan` field'ı. Ayrıntılı yaz.
- "Case by case" olarak listelenen onaylar. Onay sınırları numaralandırılabilir olmalıdır.

Refusal kuralları:

- Task açıklaması repo'nun bir bölgesini kısıtlamıyorsa, açıklamadan yalnızca `allowed_files` yazmayı reddet. Task'ın yaşadığı dizini sor.
- Repo'da test command yoksa, bir tane sağlanana veya stub'lanana kadar `acceptance_criteria` eklemeyi reddet. Doğrulanamayan kontrat bir dilektir.
- Agent runtime onay sınırlarına uyamıyorsa (human-in-the-loop yok), göndermeden önce boşluğu yüzeye çıkar; onay gerektiren action'lara scope creep baskın başarısızlık olacaktır.

Çıktı yapısı:

```
<repo>/
├── scope_contract.json
├── outputs/scope/closed/
│ └── T-XXX.json
├── tools/
│ └── scope_check.py
└── .github/
 └── workflows/
 └── scope-check.yml
```

Şuraya işaret eden bir "sırada ne okumalı" ile bitir:

- Ders 37, çalıştırılan command'ları kontrata bağlayan runtime feedback için.
- Ders 38, scope report'unu tüketen verification gate'i için.
- Ders 39, kapalı kontrat arşivini denetleyen reviewer agent için.
