---
name: skill-vit-patch-and-pos-embed-inspector
description: Bir ViT'nin yama (patch) gömme ve konumsal gömme şekillerinin modelin beklenen dizi uzunluğuyla eşleştiğini doğrulayın
version: 1.0.0
phase: 4
lesson: 14
tags: [görü-transformer, hata-ayıklama, pytorch]
---

# ViT Yama ve Konumsal Gömme Denetçisi

En yaygın ViT taşıma hatası: 224x224'te önceden eğitilmiş bir kontrol noktasını 384x384 için yapılandırılmış bir modele yüklemek (veya tersi). Konumsal gömme yanlış dizi uzunluğuna sahiptir ve model sessizce çöp üretir.

## Ne zaman kullanılır

- Önceden eğitilmiş bir ViT'yi varsayılan olmayan bir çözünürlükte ince ayar yaparken.
- ViT-B/16 ile ViT-B/32 arasındaki bir ağırlık aktarımının neden başarısız olduğunu denetlerken; denetçi yama boyutu uyumsuzluğunu işaretleyecek, böylece arayan kişi aktarımı zorlamak yerine mimariyi değiştirmesi gerektiğini bilir.
- Hatasız yüklenen ancak zayıf eğitilen bir ViT'yi ayıklarken.

## Girdiler

- `model`: somutlaştırılmış bir ViT `nn.Module`.
- `expected_image_size`: modelin üretimde göreceği H x W.
- `patch_size`: beklenen yama boyutu.

## Adımlar

1. Model içindeki yama gömme evrişimini bulun. `kernel_size`, `stride`, `in_channels`, `out_channels` değerlerini raporlayın.
2. Beklenen yama sayısını hesaplayın. Kare görüntü için: `(image_size / patch_size)^2`. Dikdörtgen için: `(H / patch_size) * (W / patch_size)`. `H % patch_size == 0` ve `W % patch_size == 0` gerektirin; aksi halde işaretleyin ve reddedin.
3. Öğrenilen konumsal gömme'yi bulun. Şeklini `(1, N, dim)` olarak raporlayın.
4. `N`'i `num_patches + 1` (CLS ile) veya `num_patches` (CLS olmadan) ile karşılaştırın. Uyumsuzluk, kontrol noktasının farklı bir çözünürlükte veya yama boyutunda önceden eğitildiği anlamına gelir.
5. Yama evrişiminin `out_channels`'ının konumsal gömme'nin `dim`'ine eşit olduğunu kontrol edin.
6. Modelin yeni çözünürlükler için konumsal gömmeleri enterpolasyon yapması gerekiyorsa, enterpolasyon yardımcısının var olduğunu doğrulayın (çoğu `timm` ViT bunu `resize_pos_embed` aracılığıyla otomatik yapar).

## Rapor

```
[vit-inspector]
  image_size:         HxW
  patch_size:         <int>
  num_patches (computed): <int>
  patch_conv:         k=<int>  s=<int>  in=<int>  out=<int>
  pos_embed shape:    (1, N, dim)
  has CLS token:      yes | no
  pos_embed N:        <int>    expected: <int>
  verdict:            ok | mismatch

[if mismatch]
  action:  yeni dizi uzunluğu için pos_embed'i yeniden başlat
  tool:    timm.models.vision_transformer.resize_pos_embed
```

## Kurallar

- Uyarı vermeden asla sessizce enterpolasyon yapma; eylemi yüzeye çıkar ki kullanıcı önceden eğitilmiş konumsal yapının kaymış olabileceğini bilsin.
- Yama boyutu uyuşmazsa, enterpolasyon önerme — doğru mimariye geç.
- Modeli yerinde düzeltmeye çalışma; raporla ve öner.
