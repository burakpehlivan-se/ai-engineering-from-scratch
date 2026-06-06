---
name: vae-trainer
description: Belirli bir veri kümesi ve alt kullanım için VAE mimarisi, gizli boyut, beta zamanlaması ve değerlendirme planı belirle
version: 1.0.0
phase: 8
lesson: 02
tags: [vae, gizli, üretken]
---

Bir veri kümesi profili (modalite, çözünürlük, veri kümesi boyutu) ve alt kullanım (yalnızca yeniden yapılandırma, örnekleme veya bir gizli-difüzyon veya token-AR model için girdi-kodlayıcı) verildiğinde, aşağıdakileri üret:

1. Varyant. Düz VAE, beta-VAE, VQ-VAE, RVQ (artıklı) veya NVAE. Modalite ve alt kullanıma bağlı tek cümlelik gerekçe.
2. Mimari. Kodlayıcı / kodçözücü topolojisi (evrişimli aşağı örnekleme faktörü, kanal genişliği, gizli boyut, dikkat blokları). Geçerli olduğunda genel referans ağırlıklarından bahset (`sd-vae-ft-ema`, Encodec, DAC, WAN-VAE).
3. Gizli boyut. Uzamsal ve kanal boyutları. Örnek başına toplam bit. Ham veriye göre sıkıştırma oranı.
4. Beta zamanlaması. Isınma rampası, son değer ve kullanılıyorsa serbest bit eşiği.
5. Değerlendirme planı. Yeniden yapılandırma MSE / SSIM / PSNR, boyut başına KL, aktif boyut sayısı, sonsal-çöküş alarm eşiği, `q(z|x)` ve önsel arasında Frechet mesafesi.

Eğitim başlangıcında beta > 0.5 ile VAE gönderme (sonsal çöküş). Görüntüler için son jeneratör olarak düz Gauss VAE kullanma — bulanık olur; bunun yerine bir difüzyon veya akış-eşleme modeli için gizli kodlayıcı olarak kullan. Kod defteri kullanımı %20'nin altında olan VQ-VAE'yi yanlış yapılandırılmış kod defteri sıfırlama politikası olarak işaretle.
