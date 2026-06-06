---
name: search-policy
description: Task shape, token budget ve evaluator kalitesi verildiğinde bir search stratejisi seç (ReAct, ToT, LATS, evolutionary).
version: 1.0.0
phase: 14
lesson: 04
tags: [tree-of-thoughts, lats, mcts, search, value-function]
---

Bir task shape (tek-yanıt / çoklu-yanıt / açık-uçlu), bir token budget ve mevcut bir evaluator (scalar test / heuristic / self-eval) verildiğinde, somut parametrelerle bir search stratejisi önerisi üret.

Şunları üret:

1. Karar. Şunlardan biri: linear ReAct, beam ToT (beam width k ile), BFS ToT (max depth ile), pruning ile DFS ToT, MCTS LATS (iteration'lar ve UCT c ile), evolutionary search (yalnızca evaluator programatik ve kontrol edilebilirse).
2. Parametreler. Her strateji için somut sayısal varsayılanlar: beam width, depth cap, branching factor K, seviye başına rollout, UCT c (varsayılan 1.4), timeout.
3. Value function. Bir node'u tam olarak neyin puanlayacağını belirt. Seçenekler: unit-test geçiş oranı, hedefe sayısal mesafe, formatlı prompted LLM skoru (sure/likely/impossible veya 1..10 veya vote) veya environment reward.
4. Token budget tahmini. En kötü durum token'lar = branching_factor ^ depth * avg_prompt_tokens. Sayıyı göster. Kullanıcının budget'ını aşıyorsa, daha ucuz bir strateji öner.
5. Başarısızlık modları. Seçilen her strateji için, en üst iki başarısızlık modunu ve onların mitigation'larını listele (örn. LATS + gürültülü evaluator -> CRITIC başına tool-grounded doğrulama ekle, Ders 05).

Sert reject sebepleri:

- Evaluator güvenilmez olduğunda search önermek (yalnızca self-eval, ground truth yok). ReAct + CRITIC'e geri dön.
- Branching factor K'yı zorlayıcı bir neden olmadan 5'in üzerine ayarlamak. K=3-5 makale varsayılanıdır; K=10 maliyeti patlatır.
- LATS'ı sohbet tarzı task'lara uygulamak. Search, programatik hedefi olmayan konuşmaya dayalı Q&A'ya yardım etmez.
- Makine-kontrol edilebilir fitness olmadan evolutionary search. AlphaEvolve sadece fitness programatik olduğunda ilginçtir (test çalıştır, hızı ölç, teorem doğrula).

Refusal kuralları:

- Token budget < tek-trajectory maliyetinin 5 katı ise, search'i reddet ve ReAct + Reflexion (Ders 03) öner.
- Wall-clock latency budget < 10 saniye ise, LATS'ı reddet ve ReAct öner.
- Task saf bilgi erişimi ise, search'i reddet ve ReWOO (Ders 02) öner.

Çıktı: bir öneri block'u (seçilen strateji, parametreler, value function, budget tahmini) artı evaluator güvenilirliği için Ders 05'e (CRITIC), evolutionary varyantlar için Ders 11'e (AlphaEvolve) veya benchmark seviyesinde doğrulama için Ders 30'a (eval-driven development) işaret eden bir "sırada ne okumalı" notu.
