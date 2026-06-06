---
name: policy-gradient-trainer
description: Belirli bir görev için REINFORCE / aktör-eleştirmen / PPO eğitim yapılandırması üret ve varyans sorunlarını teşhis et
version: 1.0.0
phase: 9
lesson: 6
tags: [rl, politika-gradyanı, reinforce]
---

Bir ortam (ayrık / sürekli eylemler, ufuk, ödül istatistikleri) verildiğinde, aşağıdakileri üret:

1. Politika başı. Softmax (ayrık) veya Gauss (sürekli) ile parametre sayıları.
2. Temel çizgi. Yok (vanilya), çalışan ortalama, öğrenilmiş `V̂(s)` veya A2C eleştirmen.
3. Varyans kontrolleri. Varsayılan olarak ödül-git, getiri normalizasyonu, gradyan kırpma değeri.
4. Entropi bonusu. Katsayı β ve azalma zamanlaması.
5. Parti boyutu. Güncelleme başına epizodlar; politika-içi veri tazeliği sözleşmesi.

> 500 adım ufukta temel çizgi olmadan REINFORCE. Softmax başı ile sürekli-eylem kontrol. `β = 0` ve gözlemlenen politika entropisi < 0.1 olan herhangi bir çalıştırmayı entropi-çökmüş olarak işaretle.

Geri dönüş. Varyans hâlâ aşırı yüksekse, bir öğrenilmiş temel değer ekle veya avantaj tahmincisine (A2C / GAE) geç.
