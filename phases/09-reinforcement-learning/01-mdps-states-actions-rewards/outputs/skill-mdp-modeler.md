---
name: mdp-modeler
description: Bir görev tanımı verildiğinde, eğitimden önce bir Markov Karar Süreci spesifikasyonu üret ve formülasyon risklerini işaretle
version: 1.0.0
phase: 9
lesson: 1
tags: [rl, mdp, modelleme]
---

Bir görev (kontrol / oyun / öneri / LLM ince-ayar) verildiğinde, aşağıdakileri üret:

1. Durum. Tam öznitelik vektörü veya tensör spesifikasyonu. Markov özelliğini gerekçelendir.
2. Eylem. Ayrık küme veya sürekli aralık. Boyutsallık.
3. Geçiş. Deterministik, bilinen modelle stokastik veya yalnızca örneklem.
4. Ödül. Fonksiyon ve kaynak. Seyrek vs şekillendirilmiş. Terminal vs adım başına.
5. İskonto. Değer ve ufuk gerekçesi.

Durum, çerçeve yığınlama veya tekrarlayan durumdan açık bahsetmeden Markov-olmayan olduğunda herhangi bir MDP'yi gönderme. Hedef sonuç açısından tanımlanmamış herhangi bir ödülü reddet. Sonsuz-ufuk görevinde `γ ≥ 1.0` olan herhangi bir değeri işaretle. Tipik adım ödülünün >100 katı olan herhangi bir ödül aralığını muhtemel gradyan-patlaması kaynağı olarak işaretle.

Ayrıca belgele: tüm MDP bileşenlerinin deterministik sürümden stokastik sürüme geçişte nasıl değiştiğini — bu, eğitimdeki kararlılık ve keşif davranışını etkiler.
