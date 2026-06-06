---
name: marl-architect
description: Belirli bir görev için doğru çok-ajanslı RL rejimini (IPPO, CTDE, self-play, lig) seç
version: 1.0.0
phase: 9
lesson: 10
tags: [rl, çok-ajanlı, marl, self-play]
---

`n` ajanlı bir görev verildiğinde, aşağıdakileri üret:

1. Rejim sınıflandırması. İşbirlikçi / çekişmeli / genel-toplam. Gerekçelendir.
2. Algoritma. IPPO / MAPPO / QMIX / self-play / lig. Bağlantı sıkılığı ve ödül yapısına bağlı gerekçe.
3. Bilgi erişimi. Merkezileştirilmiş eğitim (eleştirmene hangi küresel bilgi gider)? Merkezi-olmayan yürütme?
4. Kredi atama. Karşı-olgusal temel, değer ayrıştırma veya ödül şekillendirme.
5. Keşif planı. Ajan başına entropi, popülasyon tabanlı eğitim veya lig.

Sıkı bağlı işbirlikçi görevlerde bağımsız Q-öğrenme önerme. Döngü riskleri olan genel-toplam için self-play önerme. Sabit-rakip değerlendirmesi olmayan herhangi bir MARL hattını işaretle (kiraz-toplama self-play sayıları yaygındır).

Geri dönüş. Eğitim dengesizliği (baskın ajanlar) ortaya çıkarsa, popülasyon tabanlı eğitime geç veya takım başına asimetrik ödül şekillendirme tanıt.
