---
name: ppo-trainer
description: Belirli bir ortam için PPO eğitim yapılandırması ve teşhis planı üret
version: 1.0.0
phase: 9
lesson: 8
tags: [rl, ppo, politika-gradyanı]
---

Bir ortam ve eğitim bütçesi verildiğinde, aşağıdakileri üret:

1. Toplama boyutu. `N` ortam × `T` adım.
2. Güncelleme zamanlaması. `K` epoch, mini-parti boyutu, LR zamanlaması.
3. Vekil parametreler. `ε` (kırpma), `c_v`, `c_e`, avantaj normalizasyonu açık.
4. Avantaj. Açık `γ` ve `λ` ile GAE(`λ`).
5. Teşhis planı. KL, kırpma oranı, açıklanan varyans eşikleri uyarılarla.

`K > 30` veya `ε > 0.3` (güvensiz güven bölgesi). Avantaj normalizasyonu veya KL/kırpme izleme olmadan PPO çalıştırması. 0.4 üzerinde sürdürülen kırpme oranını sapma olarak işaretle.

Geri dönüş. Politika çökmüşse (entropi düşük, yüksek KL), `c_e`'yi 0.01-0.05'e yükselt; gradyan normları büyüyorsa, kırpmayı 0.5-1.0'a sıkılaştır.
