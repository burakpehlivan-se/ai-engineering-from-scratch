---
name: generative-model-chooser
description: Belirli bir görev ve bütçe için üretken model ailesi, omurga ve barındırılan alternatif seç
version: 1.0.0
phase: 8
lesson: 01
tags: [üretken, taksonomi]
---

Bir görev tanımı (modalite, alan, gecikme bütçesi, hesaplama bütçesi, koşullandırma sinyali) verildiğinde, aşağıdakileri üret:

1. Aile. Açık-izlenebilir, açık-yaklaşık (VAE / difüzyon), örtük (GAN), skor / akış eşleme veya token-AR. Modalite + gecikmeye bağlı tek cümlelik gerekçe.
2. Omurga + açık referans. Kullanıcının bugün ince-ayar yapabileceği önceden eğitilmiş açık-ağırlıklı bir model (ör. Stable Diffusion 3, Flux.1-dev, AudioCraft 2, StyleGAN3, 3D Gaussian Splatting).
3. Barındırılan alternatifler. Kalite / maliyet / gecikme ödünleşimine göre sıralanmış üç üretim API'si (fal.ai, Replicate, Stability, Runway, Veo, Kling, ElevenLabs vb.).
4. Başarısızlık modu. Seçilen aile için bilinen patoloji (mod çöküşü, pozlandırma yanlılığı, örnekleyici sapması, tokenlayıcı yapaylıkları, CLIP-skoru oyunu).
5. Bütçe. Tek bir A100'de yaklaşık eğitim saatleri, örnek başına çıkarım maliyeti, VRAM tabanı.

Görev olasılık puanlaması (likelihood scoring) gerektirdiğinde GAN önerme. Yüksek çözünürlüklü gerçek-zamanlı kullanım için piksel-üzeri-otoregresif önerme. Listelenen açık omurga zaten alanı kapsıyorsa "sıfırdan eğit" önerisini işaretle.
