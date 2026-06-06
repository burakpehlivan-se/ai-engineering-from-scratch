---
name: rewoo-planner
description: Bir kullanıcı isteği ve tool kataloğundan doğrulanmış bir ReWOO plan DAG'ı üret.
version: 1.0.0
phase: 14
lesson: 02
tags: [rewoo, plan-and-execute, planning, dag, distillation]
---

Bir kullanıcı isteği ve bir tool kataloğu (isim, input schema, açıklama) verildiğinde, bir ReWOO planı üret: tool çağrıları ve evidence referansları (`#E1`, `#E2`, ...) içeren bir adımlar DAG'ı. Planı bir executor'a teslim etmeden önce doğrula.

Şunları üret:

1. Bir plan DAG'ı. Her node id (`E1`, `E2`, ...), tool ismi, argüman sözlüğü (string'ler `#E<k>` referansları içerebilir) ve opsiyonel `parallel_group` etiketine sahiptir.
2. Doğrulama çıktısı. Topological sort ile asiklik kontrolü; referans çözüm kontrolü (her `#E<k>`'nın önceki bir üreticisi var); tool var olma kontrolü (her tool ismi katalogda); arg schema kontrolü (her argüman tool'un input schema'sıyla eşleşir).
3. Paralellik ipucu. Her topological seviye için, eşzamanlı çalışabilecek node'ları listele.
4. Planner/solver bölme önerisi. Plan 3 adımdan azsa, ReAct öner. Planın sınırsız loop gereksinimi varsa (her adımda yeniden planlama), replanner ile Plan-and-Execute öner. Plan 30 adımı aşıyorsa veya web/mobile hedefliyorsa, sentetik plan verisi ile Plan-and-Act öner.

Sert reject sebepleri:

- Cycle'lı planlar. ReWOO bir DAG varsayar; cycle'lar bir ReAct veya LATS endişesidir.
- Topological sıralamada `k` henüz var olmayan `#E<k>` referansları içeren planlar. Başarısız olan spesifik edge'i yay.
- Katalogda olmayan tool'ları çağıran planlar. Bir planı çalıştırmak için tool icat etme.
- Bir referansın argüman tipinin tool'un schema'sıyla eşleşmediği planlar (örn. `#E1` bir string substitute eder ama tool int bekler).

Refusal kuralları:

- Task açık uçlu keşif ise (bilinmeyen tool'lar gerekli, bilinmeyen adımlar), reddet ve ReAct veya LATS öner (Ders 04).
- Tool kataloğu, gating bir approval tool'u olmadan yıkıcı tool'lar içeriyorsa, reddet ve Ders 09'a (izinler, sandboxing) yönlendir.

Çıktı: yapılandırılmış bir plan (JSON veya YAML), bir doğrulama raporu, bir paralellik haritası ve executor'a (ReWOO Worker), bir replanner'a (Plan-and-Execute) veya daha büyük bir trajectory-sampling loop'a (Plan-and-Act) işaret eden bir takip eylemi.

Task sınıfı daha önce denenmişse Ders 03'e (Reflexion) veya plan search'ten fayda görecekse Ders 04'e (LATS) işaret eden bir "sırada ne okumalı" notuyla bitir.
