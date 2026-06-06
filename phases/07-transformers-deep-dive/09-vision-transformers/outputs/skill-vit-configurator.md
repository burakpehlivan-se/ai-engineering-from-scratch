---
name: vit-configurator
description: Yeni bir görme (vision) görevi için ViT varyantı, yama (patch) boyutu ve ön eğitim kaynağı seç
version: 1.0.0
phase: 7
lesson: 9
tags: [transformers, vit, görme]
---

Bir görme görevi (sınıflandırma / bölütleme / algılama / erişim), görüntü çözünürlüğü, veri kümesi boyutu (etiketli + etiketsiz) ve dağıtım hedefi verildiğinde, aşağıdakileri üret:

1. Omurga. Şunlardan biri: DINOv2 ViT-L/14 (erişim/sınıflandırma için varsayılan), SAM 3 kodlayıcı (bölütleme), SigLIP (görme-dil), ConvNeXt (gecikme-kritik). Tek cümlelik gerekçe.
2. Yama boyutu. 224'te standart sınıflandırma için 16, DINOv2 için 14, yüksek çözünürlükte yoğun tahmin için 8. Dizi uzunluğunu `(H/P)^2 + 1` ve dikkat maliyetini `O(N^2)` işaretle.
3. Ön eğitim kaynağı. Kontrol noktası adı. Küçük etiketli kümeler için (<10k): DINOv2 öznitelikleri dondurulmuş + doğrusal sonda. >100k için: son blokları ince-ayar yap. Nedenini belirt.
4. Eğitim reçetesi. Optimizer (AdamW), lr, artırmalar (RandAug, MixUp, Random Erasing), etiket yumuşatma (tipik 0.1), EMA.
5. Risk notu. Veri rejimi riski (tam ince-ayar için çok az veri), çözünürlük uyumsuzluğu (ön eğitim 224 → konum aradeğerlemesi olmadan dağıtım 1024), register-token eksikliği (DINOv2 özniteliklerine zarar verebilir).

1M görüntüden az veriyle ViT'i sıfırdan eğitme — CNN temel çizgileri kazanır. Flash Attention + hiyerarşik varyantları (Swin) açıkça tartışmadan 4096'yı aşan dizi uzunluğu veren yama boyutu önerme. Konumsal gömlemeleri aradeğerlemeden girdi çözünürlüğünü değiştiren herhangi bir dağıtımı işaretle.
