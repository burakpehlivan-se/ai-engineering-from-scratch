---
name: reviewer-agent
description: Builder artifact'larını okuyan, yapılandırılmış bir review raporu üreten ve insan incelemesini boş bir sayfadan değil yazılı bir sayfadan başlatan beş-boyutlu rubric ile bir reviewer agent rolü kur.
version: 1.0.0
phase: 14
lesson: 39
tags: [reviewer, rubric, role-separation, second-loop, review-report]
---

Zaten workbench artifact'ları üreten bir builder agent verildiğinde, onları okuyan ve yapılandırılmış raporlar yazan bir reviewer kur.

Şunları üret:

1. Reviewer system prompt'u ile `agents/reviewer.md`: read-only erişim, beş-boyutlu rubric, her skor için artifact path'ini alıntılamalı.
2. Workbench'ten `ReviewerInputs` yükleyen ve boyut başına LLM scorer'ı çalıştıran `tools/reviewer.py`.
3. Kanonik review rapor yolu olarak `outputs/review/<task_id>.json`.
4. Beş boyutu, her birinin yanıtladığı soruyu ve 0-1-2 anchor açıklamalarını listeleyen `docs/reviewer-rubric.md`.
5. Bir builder task'ı kapandığında review raporunu PR comment'i olarak post eden CI step'i.

Sert reject sebepleri:

- Diff'e write erişimi olan reviewer. Builder ile reviewer arasındaki boşluk bütün sinyaldir; çökertmek reliability'i yok eder.
- Skor başına anchor açıklaması olmayan rubric. Anchor'sız "0'dan 2'ye puanla" vibes'e çöker.
- Alıntıları atlayan review raporları. Her skor bir dosya veya trace entry'sine işaret etmelidir.
- Builder'ın system prompt'unu paylaşmak. Aynı model sorun değil; aynı prompt sorun.

Refusal kuralları:

- Builder verification raporu üretmiyorsa, reviewer'ı çalıştırmayı reddet. Yargı sormaya değer olmadan önce acceptance tutmalıdır.
- Projenin üçten az kapalı task'ı varsa, rubric'in kalibre edildiğini iddia etmeyi reddet. İlk raporları kalibrasyon set'i olarak sakla.
- Reviewer minimum bir güvenin altında puanlaması istenirse, reddet ve belirsiz boyunu bir insana yüzeye çıkar.

Çıktı yapısı:

```
<repo>/
├── agents/reviewer.md
├── tools/reviewer.py
├── outputs/review/
│ └── <task_id>.json
├── docs/reviewer-rubric.md
└── .github/workflows/review.yml
```

Şuraya işaret eden bir "sırada ne okumalı" ile bitir:

- Ders 40, verification + review'ı birleştiren handoff paketi için.
- Ders 41, builder/reviewer ayrımını end-to-end exercise eden real-style task için.
- Ders 05 (Self-Refine and CRITIC), bu dersin iyileştirdiği tek-agent self-review baseline'ı için.
