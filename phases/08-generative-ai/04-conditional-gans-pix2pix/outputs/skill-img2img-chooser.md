---
name: img2img-chooser
description: Eşleştirilmiş ve eşleştirilmemiş veri, alan özgüllüğü ve gecikme bütçesine göre görüntüden-görüntüye yaklaşım seç
version: 1.0.0
phase: 8
lesson: 04
tags: [pix2pix, img2img, koşullu]
---

Bir görev tanımı (kaynak alan, hedef alan, veri kullanılabilirliği - eşleştirilmiş/eşleştirilmemiş/N örnek, gecikme bütçesi, kalite çıtası) verildiğinde, aşağıdakileri üret:

1. Yaklaşım. Pix2Pix (eşleştirilmiş, dar), Pix2PixHD (eşleştirilmiş, yüksek çözünürlüklü), CycleGAN (eşleştirilmemiş), SPADE (bölütlemenden-görüntüye) veya SD3 / Flux.1 üzerinde ControlNet varyantı (genel, açık alan).
2. Eğitim veri spesifikasyonu. Minimum çift sayısı, çözünürlük, artırmalar, lisans değerlendirmeleri.
3. Mimari. G (U-Net derinliği, kanal genişliği), D (PatchGAN alıcı alanı, spektral norm), kayıp ağırlıkları (adv, L1, VGG-algısal).
4. Çıkarım gecikmesi. Tek bir tüketici GPU'da (RTX 4090, M3 Max) hedef ms/görüntü, çözünürlük ödünleşimi.
5. Değerlendirme. Ayrılan eşleştirilmiş veriye karşı LPIPS, 5k örnek üzerinde FID, göreve özgü metrikler (bölütleme görevleri için mIoU, süper-çözünürlük için PSNR), insan tercihi.

Veri eşleştirilmemiş olduğunda Pix2Pix önerme — bunun yerine CycleGAN veya ControlNet yaz. 500'den az çift ile artırma / ön eğitim tavsiyesi olmadan eşleştirilmiş model eğitme. "Keyfi metin istemi" diyen herhangi bir isteği işaretle — bunlar eşleştirilmiş GAN değil difüzyon + ControlNet gerektirir.
