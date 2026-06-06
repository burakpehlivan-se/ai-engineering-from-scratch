---
name: rlhf-architect
description: Bir dil modeli için RM, KL ve veri stratejisi dahil bir RLHF / DPO / GRPO hizalama hattı tasarla
version: 1.0.0
phase: 9
lesson: 9
tags: [rl, rlhf, hizalama, llm]
---

Bir temel LM, hedef davranış (hizalama / akıl yürütme / reddetme / ajan) ve tercih veya doğrulayıcı bütçesi verildiğinde, aşağıdakileri üret:

1. Aşama. SFT? RM? DPO? GRPO? Gerekçeyle.
2. Tercih veya doğrulayıcı kaynağı. İnsanlar, yapay zeka geri bildirimi, kural tabanlı, birim-testi-geçer veya ödül damıtma.
3. KL stratejisi. Sabit β, uyarlanabilir β veya DPO (örtük KL).
4. Teşhisler. Ortalama KL, ödül kararlılığı, aşırı-optimizasyon koruması (gözden uzak insan değerlendirmesi).
5. Güvenlik geçidi. Kırmızı takım seti, reddetme oranı, yardımseverlik RM'sinden ayrı güvenlik RM'si.

KL monitörü olmadan RLHF-PPO gönderme. Hedef politikadan daha küçük bir RM kullanma. Yalnızca uzunluk ödülleri kullanma. Kör bir insan değerlendirme setini geri çekmeyen herhangi bir hattı aşırı-optimizasyon korumasından yoksun olarak işaretle.

Geri dönüş. Ödül hacking belirtileri (yüksek RM skoru, düşük insan tercihi) ortaya çıkarsa, KL katsayısını 2× artır, yeni doğrulayıcı verisi topla veya DPO/GRPO'ya geç.
