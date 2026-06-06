---
name: feedback-runner
description: Shell command'larını deterministik stdout/stderr/exit/duration capture ile sar, command başına bir JSONL kaydı persist et ve feedback eksik olduğunda agent loop'unun ilerlemesini reddet.
version: 1.0.0
phase: 14
lesson: 37
tags: [feedback, subprocess, runner, jsonl, loop-control]
---

Bir agent loop'u içinde shell command çalıştıran bir proje verildiğinde, bir feedback runner'ı ve yazdığı JSONL'i üret.

Şunları üret:

1. `run_with_feedback(command: list[str], agent_note: str, timeout_s: float) -> FeedbackRecord` açığa çıkaran `tools/run_with_feedback.py`.
2. Workbench altında `feedback_record.jsonl` konumu, satır başına bir kayıt.
3. Aktif task için en son N kaydı döndüren `tools/feedback_loader.py`.
4. Agent loop'unun success iddia etmeden önce çağırdığı bir `loop_can_advance(record) -> bool` helper'ı.
5. Şunları kapsayan testler: success path, sıfır-olmayan exit, timeout, eksik binary, deterministik head/tail truncation.

Sert reject sebepleri:

- Runner'ın herhangi bir yerinde `shell=True`. Sadece argv.
- Wall clock'a veya rastgele örneklemeye bağlı truncation. Aynı input aynı kaydı üretmelidir.
- `duration_ms` olmadan kayıtlar. Yavaş probe'lar workbench'in takılmasının ilk işaretidir.
- Sınırsız bir liste döndüren loader. Son N ile cap'le veya paginate et.

Refusal kuralları:

- Proje stdout üzerinden secret'ları pipe'luyorsa, bir redaction adımı olmadan runner'ı göndermeyi reddet. Yakalanmış olacak satırları yüzeye çıkar.
- Projede süresiz takılabilen command'lar varsa, bir default timeout ve açık bir override listesi olmadan göndermeyi reddet.
- Runner paylaşılan state'li bir worker içinde çalışıyorsa, JSONL append etrafında bir file lock'u atlamayı reddet. Birden çok writer dosyayı yırttıracaktır.

Çıktı yapısı:

```
<repo>/
├── feedback_record.jsonl
└── tools/
    ├── run_with_feedback.py
    ├── feedback_loader.py
    └── test_feedback_runner.py
```

Şuraya işaret eden bir "sırada ne okumalı" ile bitir:

- Ders 38, kayıtları tüketen verification gate'i için.
- Ders 39, bir run'ı skorlarken feedback'i okuyan reviewer agent için.
- Ders 23, feedback sağlam olduğunda telemetry tarafına eklemek için OTel GenAI conventions'ı.
