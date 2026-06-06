---
name: attention-shapes
description: Dikkat (attention) uygulamalarındaki şekil (shape) hatalarını ayıklar.
phase: 5
lesson: 10
---

Bozuk bir dikkat uygulaması verildiğinde şekil uyumsuzluğunu tespit edersiniz. Çıktı:

1. Hangi matrisin şekli yanlış. Tensörü adlandırın.
2. Şeklinin ne olması gerektiği, `(d_s, d_h, d_attn, T_enc, T_dec, batch_size)` değerlerinden türetilir.
3. Tek satırlık düzeltme. Transpoze, reshape veya projeksiyon.
4. Regresyonları yakalayacak bir test. Genellikle `output.shape == (batch, T_dec, d_h)` ve `weights.shape == (batch, T_dec, T_enc)` olduğunu ve `weights.sum(dim=-1)` değerinin 1'e yakın olduğunu doğrulayın.

Sessizce yayın yapan (broadcast) düzeltmeleri önermeyi reddedin. Broadcast-gizleyen hatalar sonra sessiz doğruluk düşüşü olarak ortaya çıkar.

Bahdanau karışıklığı için, kod çözücü girdisinin `s_{t-1}` (adım öncesi durum) olduğunu ısrar edin. Luong için, `s_t` (adım sonrası durum). Nokta çarpımı dikkatinde en yaygın ilk-sefer hatası sorgu/anahtar boyut uyumsuzluğudur — bunu açıkça işaretleyin.
