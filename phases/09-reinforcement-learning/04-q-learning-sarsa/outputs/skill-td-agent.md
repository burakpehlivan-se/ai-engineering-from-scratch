---
name: td-agent
description: Tablo veya küçük-öznitelikli bir RL görevi için Q-öğrenme, SARSA, Beklenen SARSA arasında seç
version: 1.0.0
phase: 9
lesson: 4
tags: [rl, td-öğrenme, q-öğrenme, sarsa]
---

Tablo veya küçük-öznitelikli bir ortam verildiğinde, aşağıdakileri üret:

1. Algoritma. Q-öğrenme / SARSA / Beklenen SARSA / n-adım varyantı. Politika-içi ve politika-dışı ve varyansa bağlı tek cümlelik gerekçe.
2. Hiperparametreler. α, γ, ε, azalma zamanlaması.
3. Başlatma. Q_0 değeri (iyimser vs sıfır) ve gerekçe.
4. Yakınsama teşhisi. Hedef öğrenme eğrisi, DP mümkünse `|Q - Q*|` kontrolü.
5. Dağıtım uyarısı. Çıkarımda keşif nasıl davranacak? SARSA'nın muhafazakarlığı gerekli mi?

> 10⁶ durum uzayına tablo TD uygulama. Maks-yanlılık uyarısı olmadan Q-öğrenme ajanı gönderme. Eğitim boyunca ε 1.0'da tutulan herhangi bir ajanı işaretle (sömürü aşaması yok).

Geri dönüş. Politika-dışı (Q-öğrenme) keşif-yanlılığı üretiyorsa, SARSA'ya geç veya çift öğrenme ajanı kullan.
