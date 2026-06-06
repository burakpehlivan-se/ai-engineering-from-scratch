---
name: fm-tuner
description: Bir difüzyon eğitim planını akış-eşleme / düzeltilmiş-akış yapılandırmasına dönüştür
version: 1.0.0
phase: 8
lesson: 13
tags: [akış-eşleme, düzeltilmiş-akış, difüzyon]
---

Difüzyon tarzı bir eğitim planı (veri, hesaplama, zamanlama, hedef adım sayısı, kalite çıtası) verildiğinde, bir akış-eşleme eşdeğerini üret:

1. Zamanlama + interpolant. Doğrusal (düzeltilmiş akış), optimal taşıma (Lipman OT-CFM), varyans-koruyan veya kosinüs. Tek cümlelik gerekçe.
2. Zaman örneklemesi. Düzgün, logit-normal (SD3) veya mod-ağırlıklı. 1000 Hz'de düzgün örnekleme uç noktalarda kapasiteyi boşa harcadığında uyar.
3. Hedef. Hız v = x_1 - x_0 (düzeltilmiş akış) veya alfa'(t)x_1 + sigma'(t)x_0 (CFM). Hangisi olduğunu belirt.
4. Optimizer + lr ısınma. Transformer ölçeğinde kararlılık için beta2 = 0.95 ile AdamW dahil.
5. Yeniden akış planı. 0, 1 veya 2 yeniden akış yinelemesi çalıştırılıp çalıştırılmayacağı; yineleme başına bütçe ~ düzenlenmiş bir alt küme üzerinde tam yeniden çıkarım.
6. Adım sayıları. Eğitim adım sayısı hedefi, beklenen çıkarım adımları (20, 4, 2, 1), yönlendirme ölçeği aralığı.
7. Değerlendirme. Difüzyon temel çizgisine karşı FID / CLIP-skoru, adım sayısına karşı kalite grafiği.

v_1 yakınsamadan önce yeniden akış yapma (kötü bir model üzerinde yeniden akış sadece kötü yönü içine işler). Tutarlılık damıtma olmadan 1 adımlık çıkarım önerme. >20 adımlık çıkarım hedefleyen herhangi bir akış-eşleme modelini işaretle - o kadar çok adıma ihtiyacınız varsa, reformülasyonu boşa harcadınız.

Geri dönüş. Yeniden formülasyon tutmazsa, difüzyon zamanlamasına geri dön ve v_1'i aynı bütçeyle eğit; eşleme seçimi (Lipman OT-CFM) eğitim sırasında yalnızca küçük avantajlar sağlar.
