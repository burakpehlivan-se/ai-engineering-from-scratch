---
name: skill-heatmap-to-coords
description: Her üretim poz modeli tarafından kullanılan alt-piksel ısı haritasından-koordinata rutinini yazın
version: 1.0.0
phase: 4
lesson: 21
tags: [anahtar-nokta, poz, alt-piksel, çıkarım]
---

# Isı Haritasından Koordinatlara

Ham anahtar nokta ısı haritalarını alt-piksel hassas koordinatlara dönüştürün. Her poz işlem hattındaki en ucuz doğruluk yükseltmesi.

## Ne zaman kullanılır

- Isı haritası tabanlı bir anahtar nokta modeli dağıtırken.
- Poz metriklerini kıyaslarken — OKS, alt-piksel doğruluğuna son derece duyarlıdır.
- Poz kodunu bir framework'ten diğerine taşırken.

## Girdiler

- `heatmaps`: `(N, K, H, W)` tensör, modelden anahtar nokta başına ısı haritaları.
- `confidence_threshold`: tepesi bu değerin altında olan anahtar noktaları at.

## Adımlar

1. Her ısı haritasının **argmax**'ını alarak tamsayı tepe konumunu bulun.
2. **Birinci-fark ofseti** — komşu piksellerden alt-piksel ofseti tahmin edin. `0.25` katsayısı, `sigma >= 1` ile Gaussian ısı haritaları için kalibre edilmiş bir buluşsal yöntemdir; ilkeli alt-piksel kurtarma için tam bir kuadratik uyum (DARK) veya bir Gaussian uyumu kullanın.

```
dx = 0.25 * sign(heatmap[y, x+1] - heatmap[y, x-1])
dy = 0.25 * sign(heatmap[y+1, x] - heatmap[y-1, x])
```

DARK / kuadratik varyant için, yerel bir kuadratik kullanarak yaklaşık hesaplayın:

```
dx = -0.5 * (heatmap[y, x+1] - heatmap[y, x-1])
 / (heatmap[y, x+1] - 2 * heatmap[y, x] + heatmap[y, x-1] + eps)
```

Kuadratik uyum, sivri ısı haritalarında daha doğrudur; işaret tabanlı ofset, ısı haritaları gürültülü olduğunda daha güvenli varsayılan olarak kabul edilir.

3. **Ofset ekleyin** tamsayı tepesine.
4. **Güven** — anahtar nokta başına tepe değerini döndürün; istemciler düşük güvenli tahminleri maskelemek için kullanır.
5. **Sınır durumu** — tepe bir eksen boyunca ilk veya son piksele düştüğünde, komşulardan biri sıkıştırılır; ofset sıfıra çöker, bu da en güvenli geri dönüştür.

## Çıktı şablonu

```python
import torch

def heatmap_to_coords_subpixel(heatmaps, threshold=0.2):
 N, K, H, W = heatmaps.shape
 flat = heatmaps.reshape(N, K, -1)
 conf, idx = flat.max(dim=-1)
 ys = (idx // W).float()
 xs = (idx % W).float()

 ys_int = ys.long()
 xs_int = xs.long()

 x_minus = (xs_int - 1).clamp(min=0)
 x_plus = (xs_int + 1).clamp(max=W - 1)
 y_minus = (ys_int - 1).clamp(min=0)
 y_plus = (ys_int + 1).clamp(max=H - 1)

 batch_idx = torch.arange(N).view(-1, 1).expand(-1, K)
 kp_idx = torch.arange(K).view(1, -1).expand(N, -1)

 dx_raw = (heatmaps[batch_idx, kp_idx, ys_int, x_plus]
 - heatmaps[batch_idx, kp_idx, ys_int, x_minus])
 dy_raw = (heatmaps[batch_idx, kp_idx, y_plus, xs_int]
 - heatmaps[batch_idx, kp_idx, y_minus, xs_int])
 dx = 0.25 * torch.sign(dx_raw)
 dy = 0.25 * torch.sign(dy_raw)

 at_left = xs_int == 0
 at_right = xs_int == (W - 1)
 at_top = ys_int == 0
 at_bottom = ys_int == (H - 1)
 dx = torch.where(at_left | at_right, torch.zeros_like(dx), dx)
 dy = torch.where(at_top | at_bottom, torch.zeros_like(dy), dy)

 refined_x = xs + dx
 refined_y = ys + dy
 coords = torch.stack([refined_x, refined_y], dim=-1)
 mask = conf >= threshold
 return coords, conf, mask
```

## Rapor

```
[subpixel decode]
 keypoints: K
 threshold: <float>
 valid_rate: eşiğin üzerindeki anahtar noktaların oranı
```

## Kurallar

- Komşu endekslerini her zaman geçerli aralığa sıkıştırın; kenar dışı anahtar noktalar sıfır-fark ofsetine sahiptir ancak çökme yoktur.
- İstemciler düşük güvenli noktaları maskeleyebilsin diye koordinatlarla birlikte güveni de döndürün.
- Alt-piksel iyileştirme yalnızca ısı haritası tepe etrafında pürüzsüz olduğunda yardımcı olur — eğitimin sigma >= 1 ile bir Gaussian hedef kullandığını kontrol edin.
- Çok küçük ısı haritası çözünürlükleri (< 48x48) için, koordinatları çıkarmadan önce ısı haritasını tam görüntü boyutuna yükseltmeyi düşünün; alt-piksel ofset adımla ölçeklenir.
