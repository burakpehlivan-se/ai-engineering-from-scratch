---
name: marl-picker
description: Belirli bir çok-agent'lı görev için bir MARL (Multi-Agent Reinforcement Learning) algoritması (MADDPG, QMIX, MAPPO, IQL veya uzantıları) seçin. İşbirlikçi vs rekabetçi, eylem-uzayı türü, heterojenlik, ödül yapısı ve ölçeği göz önünde bulundurun.
version: 1.0.0
phase: 16
lesson: 20
tags: [multi-agent, MARL, MADDPG, QMIX, MAPPO, CTDE]
---

Bir çok-agent'lı görev tanımı verildiğinde, MARL algoritmasını seçin.

Üretin:

1. **Görev taksonomisi.** Tamamen işbirlikçi (paylaşılan ödül), tamamen rekabetçi (sıfır-toplam), karışık, genel-toplam. Agent sayısı. Homojen vs heterojen.
2. **Gözlemlenebilirlik.** Tam (her agent küresel durumu görür), kısmi (her biri yalnızca kendi gözlemini görür) veya iletişim-etkin.
3. **Eylem uzayı.** Ayrık (Atari-benzeri, SMAC) veya sürekli (parçacık dünyası, MuJoCo). Algoritma seçimini etkiler.
4. **Ödül yapısı.** Yoğun (adım başına şekillendirilmiş) vs seyrek (yalnızca terminal). Yoğun, MAPPO'yu pratik yapar; seyrek, kredi atama yardımına ihtiyaç duyar (QMIX'in değer ayrıştırması).
5. **Algoritma önerisi.** Yu ve ark. 2022'ye göre temel olarak MAPPO ile başlayın. Şuna geçin:
 - İşbirlikçi + homojen + güçlü seyrek-ödül kredi ataması gerektiğinde → QMIX
 - Karışık (işbirlikçi + rekabetçi) + sürekli eylemler → MADDPG
 - Monotonluk kısıtı çok kısıtlayıcı olduğunda → Uzantılar (QTRAN, QPLEX, FACMAC)
6. **Eğitim altyapısı.** Sahip misiniz: yeterli etkileşim verisi, hesaplama bütçesi, ödül şekillendirme uzmanlığı, stabilite bütçesi (deney başına 5-10 tohum)? Değilse, LLM agent'ları için prompt-düzeyinde politikalar önerin.
7. **Deployment sözleşmesi.** CTDE (Centralized Training, Decentralized Execution — Merkezi Eğitim, Merkezi-Olmayan Yürütme): deploy zamanında her agent yalnızca yerel gözlemi görür. Çalışma-zamanı kodunun buna uyduğu sözleşmeyi açıkça yazın.

Keskin redler:

- İlk çalıştırma için MAPPO-dışı bir temel seçmek. MAPPO 2026 temelidir; oradan başlayın.
- Karışık işbirlikçi-rekabetçi görevler için QMIX. Değer ayrıştırması monoton toplama varsayar.
- Etkileşim verisi veya ödül sinyali olmayan LLM-agent sistemleri için MARL eğitimi önerilmesi. Prompt-düzeyinde politikalar veri gelene kadar daha iyi performans gösterecektir.
- Agent başına gözlem ve eylemleri loglamadan eğitim. Hata ayıklama imkansızdır.

Ret kuralları:

- Görevin 1000 bölümün altında etkileşim verisi varsa, prompt-düzeyinde politikalar veya denetimli ince-ayar önerin.
- Görev Markov-olmayan ise (bellek gerektirir) ancak öneri tekrarlayan eleştirmenler içermiyorsa, boşluğu işaretleyin.
- Görev genel-toplam rekabetçi ise (birden fazla denge), MARL tek başına birini seçmez; mekanizma tasarımı veya denge seçimi önerin.

Çıktı: Tek sayfalık özet. Tek cümlelik bir öneriyle başlayın ("Merkezi değer fonksiyonuyla MAPPO temeli; agent başına ayrık aktör; deploy'da CTDE; deney başına 5 tohum."), sonra yukarıdaki yedi bölüm. Eğitimden-deploy'a bir pipeline ile bitirin: veri toplama, eğitim, değerlendirme, dağıtım.
