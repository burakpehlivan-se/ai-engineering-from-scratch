---
name: orchestration-picker
description: Verilen bir problem için bir orchestration topology (supervisor, swarm, hierarchical, debate veya none) seç ve minimal olarak implemente et.
version: 1.0.0
phase: 14
lesson: 28
tags: [orchestration, supervisor, swarm, hierarchical, debate]
---

Bir ürün domain'i ve bir task sınıfı verildiğinde, minimal topology'yi seç.

Karar:

1. 1 agent + workflow pattern'leri (Ders 12) yeterli mi? -> Hiç topology kullanma.
2. Farklı sorumlulukları olan 2-4 specialist mı? -> **supervisor-worker**.
3. Latency-critical ve specialist'lar temiz handoff yapabiliyor mu? -> **swarm**.
4. 10+ specialist, supervisor context bütçesi başarısız mı? -> **hierarchical**.
5. Maliyetten çok accuracy önemli, multi-proposer + critique yardımcı mı? -> **debate** (Ders 25).

Şunları üret:

1. Seçilen topology iskelesi.
2. Swarm'da hop counter; hierarchical'da nesting depth limit; debate'ta round cap.
3. Handoff başına veya adım başına observability hook'ları (OTel GenAI span'ları, Ders 23).
4. Bir "neden bu, neden o değil" README bölümü.

Sert reject sebepleri:

- Sırayla 3 LLM çağrısını "multi-agent" olarak adlandırmak. Bu bir prompt chain'dir.
- Hop counter olmadan swarm. Bouncing bir kesinliktir.
- Branch başına 1 specialist'te bottom out eden hierarchical. Düzleştir.

Refusal kuralları:

- Kullanıcı tek bir ReAct loop'un hallettiği bir task için multi-agent isterse, reddet ve Ders 01'i öner.
- Kullanıcı 2 adımlık bir task için supervisor isterse, reddet ve prompt chaining (Ders 12) öner.
- Domain'in compliance / audit gereksinimleri varsa, swarm'ı reddet ve supervisor veya hierarchical öner.

Çıktı: topology iskelesi + karar gerekçesiyle birlikte README. Supervisor implementasyonu için Ders 13'e (LangGraph), handoffs-as-tools için Ders 16'ya (OpenAI Agents SDK) veya debate specifics için Ders 25'e işaret eden bir "sırada ne okumalı" ile bitir.
