---
name: game-rl-designer
description: Belirli bir alan için bir oyun-RL veya akıl yürütme-RL eğitim hattı (AlphaZero / MuZero / GRPO) tasarla
version: 1.0.0
phase: 9
lesson: 12
tags: [rl, alphazero, muzero, grpo, self-play]
---

Bir hedef (mükemmel-bilgi oyunu / mükemmel-olmayan-bilgi / Atari / LLM akıl yürütme / kombinatoryal) verildiğinde, aşağıdakileri üret:

1. Ortam uyumu. Bilinen kurallar? Markov? Stokastik? Çok-ajanlı? AlphaZero vs MuZero vs GRPO'yu bilgilendirir.
2. Arama stratejisi. MCTS (öğrenilmiş öncelikle PUCT), Gumbel örneklenmiş, en-iyi-N veya hiçbiri.
3. Self-play planı. Simetrik self-play / lig / çevrimdışı veri / doğrulayıcı-üretilmiş.
4. Hedef sinyal. Oyun sonucu / doğrulayıcı ödülü / tercih / öğrenilmiş model. Sağlamlık planı dahil.
5. Teşhisler. Temel çizgiye karşı kazanma oranı, ELO eğrisi, doğrulayıcı geçme oranı, referansa KL.

Mükemmel-olmayan-bilgi oyunlarında AlphaZero (CFR'ye yönlendir). Güvenilir doğrulayıcı olmadan GRPO. Sabit temel rakip seti olmadan herhangi bir oyun-RL hattı (self-play ELO aksi takdirde kalibrasyonsuz).

Geri dönüş. Self-play mod çöküşü (aynı açılışlara yakınsama) gösteriyorsa, Dirichlet gürültüsünü artır veya lig eğitimine geç.
