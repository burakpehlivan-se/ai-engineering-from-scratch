---
name: dqn-trainer
description: Ayrık-eylem bir RL görevi için DQN eğitim yapılandırması (tampon, hedef senkronizasyonu, ε zamanlaması, ödül kırpma) üret
version: 1.0.0
phase: 9
lesson: 5
tags: [rl, dqn, derin-rl]
---

Ayrık-eylemli bir ortam (gözlem şekli, eylem sayısı, ufuk, ödül ölçeği) verildiğinde, aşağıdakileri üret:

1. Ağ. Mimari (MLP / CNN / Transformer), öznitelik boyutu, derinlik.
2. Tekrar tamponu. Kapasite, mini-parti boyutu, ısınma boyutu.
3. Hedef ağ. Senkronizasyon stratejisi (her C adımda sert veya yumuşak τ).
4. Keşif. ε başlangıç / bitiş / zamanlama uzunluğu.
5. Kayıp. Huber vs MSE, gradyan kırpma değeri, ödül kırpma kuralı.
6. Çift DQN. Açık neden olmadıkça varsayılan olarak açık.

Hedef ağı, tekrar tamponu olmayan veya ε 1'de tutulan DQN gönderme. Sürekli-eylem görevlerini reddet (SAC / TD3'e yönlendir). Adım başına ortalamanın >10× ödül aralığını kırpma veya ölçek normalizasyonu gerektiren şekilde işaretle.

Geri dönüş. Q değerleri şişiyorsa veya kararsızsa, gradyan kırpmayı 0.5–1.0'a sıkılaştır, öğrenme oranını yarıya düşür veya noisy net keşfine geç.
