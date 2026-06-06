---
name: stylegan-inversion
description: Önceden eğitilmiş StyleGAN üzerinde gerçek bir fotoğraf için tersine çevirme ve düzenleme hattı seç
version: 1.0.0
phase: 8
lesson: 05
tags: [stylegan, tersine-çevirme, düzenleme]
---

Gerçek bir fotoğraf + önceden eğitilmiş StyleGAN kontrol noktası (FFHQ-1024, StyleGAN-XL, özel ince-ayar) ve hedef düzenleme (yaş, gülümseme, poz, saç, kimlik koruma) verildiğinde, aşağıdakileri üret:

1. Tersine çevirme yöntemi. e4e (hızlı, düşük sadakat), ReStyle (yinelemeli kodlayıcı), HyperStyle (hiperağ), PTI (çevirsel ayar) veya doğrudan W optimizasyonu. Sadakat ve hıza bağlı tek cümlelik gerekçe.
2. Hedef uzay. W, W+ veya StyleSpace. Ödünleşimler: W = en ayrıştırılmış ama en düşük sadakat, W+ = katman başına w, StyleSpace = kanal düzeyinde.
3. Düzenleme yönü. Adlandırılmış yön kaynağı: InterFaceGAN (SVM tabanlı), StyleSpace kanalları, GANSpace PCA veya öğrenilmiş sınıflandırıcı.
4. Sadakat bütçesi. Kimlik kaymasından önce LPIPS eşiği; geri alma sezgiseli.
5. Değerlendirme. ID benzerliği (ArcFace kosinüs), orijinale LPIPS, düzenleme gücü (hedef öznitelik sınıflandırıcı skoru).

Doğrudan Z'de düzenleme yapan herhangi bir hattı reddet (dolaşık). Kimlik kontrolleri olmadan büyük düzenlemeleri (>1.5 sigma W) reddet. Açık alan düzenleme gerektiren istekleri işaretle (ör. "onu çizgi filme çevir") — bunlar difüzyon + IP-Adapter gerektirir, StyleGAN değil.
