---
name: diffusion-trainer
description: Bir difüzyon eğitim çalıştırmasını yapılandır: zamanlama, tahmin hedefi, örnekleyici ve değerlendirme planı
version: 1.0.0
phase: 8
lesson: 06
tags: [difüzyon, ddpm, eğitim]
---

Bir veri kümesi profili (modalite, çözünürlük, veri kümesi boyutu), hesaplama bütçesi (GPU saat, VRAM tabanı) ve kalite çıtası (FID hedefi veya alt kullanım) verildiğinde, aşağıdakileri üret:

1. Zamanlama. Doğrusal, kosinüs (Nichol) veya sigmoid. T adım sayısı (DDPM temel çizgisi için 1000; daha hızlı varyantlar için 256).
2. Tahmin hedefi. epsilon, v-tahmini veya x_0. Zamanlama boyunca çözünürlük ve sinyal-gürültü oranına bağlı gerekçe.
3. Mimari. Piksel difüzyonu için U-Net derinliği + kanal genişliği, gizli difüzyon için DiT veya video için 3D U-Net / DiT. Zaman gömme şemasını dahil et (sinüzoidal + MLP, FiLM veya AdaLN).
4. Örnekleyici. DDIM (20-50 adım), DPM-Solver++ (10-20), Euler-A (yaratıcı) veya damıtılmış 1-4 adım. Yönlendirme ölçeği (CFG w) önerisini dahil et.
5. Değerlendirme planı. FID / KID / CLIP-skoru / insan-tercihi, örnek sayılarıyla (FID için >=10k), CFG w için tarama protokolü.

Gizli difüzyon aynı kaliteyi FLOP'ların 1/16'sında elde ederken piksel-uzayı difüzyonunu >=256x256'da eğitmeyi önerme. Koşullu üretim için CFG olmadan model gönderme — koşullu modelden sıfır-atış koşulsuz örnekler genellikle dejeneredir. beta_T > 0.1 olan herhangi bir zamanlamayı muhtemelen doygun veya kararsız eğitim üretecek şekilde işaretle.
