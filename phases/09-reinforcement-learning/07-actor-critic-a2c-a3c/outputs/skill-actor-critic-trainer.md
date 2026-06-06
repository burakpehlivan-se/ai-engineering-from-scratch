---
name: actor-critic-trainer
description: Avantaj tahmini ve kayıp ağırlıkları belirtilen bir ortam için A2C / A3C / GAE yapılandırması üret
version: 1.0.0
phase: 9
lesson: 7
tags: [rl, aktör-eleştirmen, gae]
---

Bir ortam ve hesaplama bütçesi verildiğinde, aşağıdakileri üret:

1. Paralellik. A2C (GPU partili) vs A3C (CPU eşzamansız) ve işçi sayısı.
2. Toplama uzunluğu T. Güncelleme başına ortam başına adım.
3. Avantaj tahmincisi. n-adım veya GAE(λ); λ belirt.
4. Kayıp ağırlıkları. `c_v` (değer), `c_e` (entropi), gradyan kırpma.
5. Öğrenme oranları. Aktör ve eleştirmen (kullanılıyorsa ayrı).

Ufuk > 1000 olan ortamlarda tek-işçili A2C (çok politika-içi, çok yavaş). Avantaj normalizasyonu olmadan gönderme. `c_e = 0` ve gözlemlenen entropi < 0.1 olan herhangi bir çalıştırmayı entropi-çökmüş olarak işaretle.

Geri dönüş. Politika yeterince güncellenmiyorsa (yavaş öğrenme), işçi sayısını artır veya T'yi düşür; çok fazla politika-içi sapma varsa, GAE λ'sını 0.9-0.95'e artır.
