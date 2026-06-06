---
name: hybrid-planner
description: Policy-bound iş akışları için kanıtlanabilir şekilde doğru planlar üretmek üzere ChatHTN'yi, kod araması için makine tarafından kontrol edilebilir bir evaluator ile AlphaEvolve'u kapsayan hibrit bir planner üret ve problem için doğru olanı seç.
version: 1.0.0
phase: 14
lesson: 11
tags: [planning, htn, chathtn, alphaevolve, evolutionary-search]
---

Bir problem sınıfı (policy-bound workflow, code optimization veya open-ended task) verildiğinde, bir planner seç ve doğru bir iskele üret.

Karar:

1. Problemde sert preconditions / policy / scheduling kısıtları var mı? -> HTN (ChatHTN).
2. Problemde deterministik, makine tarafından kontrol edilebilir bir fitness function var mı? -> Evolutionary (AlphaEvolve).
3. Hiçbiri değil mi? -> Bunun yerine ReAct (Ders 01) veya ReWOO (Ders 02) kullan.

HTN için şunları üret:

1. `preconditions`, `effects_add`, `effects_remove` alanlarına sahip `Operator` tipi.
2. `task`, `preconditions`, `subtasks` alanlarına sahip `Method` tipi.
3. Önce method'ları deneyen, LLM decomposition'a geri dönen ve başarılı LLM decomposition'larını cache'leyen bir planner.
4. Bilinmeyen operator veya method'lara referans veren LLM decomposition'larını reddeden bir validation adımı.

Evolutionary için şunları üret:

1. Aday programlardan oluşan bir seed population.
2. Skalar fitness döndüren deterministik bir evaluator.
3. Bir mutation operator'ı (LLM-güdümlü veya kural tabanlı).
4. Early stopping içeren bir selection loop'u (top-k'yı tut, mutasyona uğrat, tekrarla).

Sert reject sebepleri:

- LLM çıktısının operator-schema doğrulaması olmadan doğrudan uygulandığı ChatHTN. Soundness iddiası çöker.
- Evaluator'ın LLM judge çağırdığı AlphaEvolve. Fitness deterministik olmalıdır; LLM judge'lar loop'un toparlayamayacağı stokastik gürültü getirir.
- Açık-uçlu task'lar için iki pattern de ("blog yazısı yaz"). Evaluator yok, precondition yok -> ReAct kullan.

Refusal kuralları:

- Domain'de açık bir operator schema'sı yoksa, ChatHTN'yi reddet. ReWOO veya düz ReAct öner.
- Domain'de makine tarafından kontrol edilebilir fitness yoksa, AlphaEvolve'u reddet. Self-Refine (Ders 05) öner.
- Kullanıcı "planner + LLM nihai kararı verir" isterse, reddet. Sembolik doğruluk ile LLM keşfi arasındaki bölünme yük taşıyıcıdır.

Çıktı: `operators.py`, `methods.py`, `planner.py` (HTN) veya `evaluator.py`, `mutator.py`, `loop.py` (evolutionary), artı karar gerekçesini açıklayan bir `README.md`. Problem debate şeklinde doğrulamaya uygunsa Ders 25'e, task aslında ReWOO şeklindeyse Ders 02'ye işaret eden bir "sırada ne okumalı" ile bitir.
