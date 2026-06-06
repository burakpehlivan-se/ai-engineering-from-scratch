---
name: skill-depth-to-pointcloud
description: Doğru intrinsik işleme ile derinlik haritalarından nokta bulutları oluşturun ve .ply'ye dışa aktarın
version: 1.0.0
phase: 4
lesson: 26
tags: [derinlik, nokta-bulutu, 3d, intrinsikler]
---

# Derinlikten Nokta Bulutuna

Bir derinlik haritası artı bir renkli görüntüyü dokulu bir nokta bulutuna dönüştürün, görselleştirme veya daha ileri 3D çalışmaları için dışa aktarılabilir.

## Ne zaman kullanılır

- Derinlik tahminlerini gerçek bir 3D sahne olarak görselleştirirken.
- Tek bir görüntüden seyrek bir 3D yeniden yapılandırmayı önyüklerken.
- SfM başarısız olduğunda 3DGS eğitimi için girdi üretirken.
- Tahmin edilen derinliği LiDAR temel doğruluğuna karşı karşılaştırırken.

## Girdiler

- `depth`: çıktıda istediğiniz aynı birimlerde derinliklerin `(H, W)` numpy dizisi (metre önerilir).
- `rgb`: `(H, W, 3)` numpy dizisi renkler (uint8 veya float32 [0, 1]).
- `intrinsics`: piksel birimlerinde `(fx, fy, cx, cy)`.
- İsteğe bağlı `depth_scale`: tahmin edilen derinlik birimlerini metreye dönüştürmek için çarpan.

## İşlem hattı

1. **Doğrulayın** — derinlik, dahil etmeyi planladığınız her yerde pozitif ve sonlu olmalıdır. Geçersiz pikselleri maskeleyin.
2. **Kaldırın** — piksel başına `X = (u - cx) * d / fx`, `Y = (v - cy) * d / fy`, `Z = d`.
3. **RGB ile eşleştirin** — her 3D nokta eşleşen pikselden bir `(r, g, b)` üçlüsü alır.
4. **Dışa aktarın** — PLY (taşınabilir), `.xyz` (hafif), `.pcd` (Open3D-yerel), `.las`/`.laz` (coğrafi-uzamsal).

## Uygulama şablonu

```python
import numpy as np

def depth_to_point_cloud(depth, intrinsics, depth_scale=1.0, min_depth=0.1, max_depth=100.0):
    H, W = depth.shape
    fx, fy, cx, cy = intrinsics
    v, u = np.meshgrid(np.arange(H), np.arange(W), indexing="ij")
    z = depth.astype(np.float32) * depth_scale
    valid = (z > min_depth) & (z < max_depth) & np.isfinite(z)
    x = (u - cx) * z / fx
    y = (v - cy) * z / fy
    points = np.stack([x, y, z], axis=-1)
    return points, valid


def write_ply(path, points, colors=None, valid_mask=None):
    p = points.reshape(-1, 3)
    if valid_mask is not None:
        p = p[valid_mask.flatten()]
    lines = [
        "ply",
        "format ascii 1.0",
        f"element vertex {p.shape[0]}",
        "property float x", "property float y", "property float z",
    ]
    if colors is not None:
        c = colors.reshape(-1, 3).astype(np.uint8)
        if valid_mask is not None:
            c = c[valid_mask.flatten()]
        lines += ["property uchar red", "property uchar green", "property uchar blue"]
    lines.append("end_header")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
        if colors is not None:
            for pt, col in zip(p, c):
                f.write(f"{pt[0]:.4f} {pt[1]:.4f} {pt[2]:.4f} {col[0]} {col[1]} {col[2]}\n")
        else:
            for pt in p:
                f.write(f"{pt[0]:.4f} {pt[1]:.4f} {pt[2]:.4f}\n")
```

## Rapor

```
[export]
  input depth shape:  (H, W)
  valid points:       <H*W>'den <N>
  output format:      ply | xyz | pcd | las
  coordinate system:  camera (+X sağ, +Y aşağı, +Z ileri)
  scale:              metres | millimetres | normalised
```

## Kurallar

- Geçersiz derinliği (sıfır, NaN, inf, doygun) her zaman maskeleyin; bunları dahil etmek orijinde bir çöp noktalar bulutu üretir.
- Göreli bir derinlik modelinden tahmin için, metrik olarak dışa aktarmayın; çıktı dosya adının önüne sözleşmeyi işaretlemek için `relative_` ekleyin.
- Kamera koordinat sözleşmesini tutarlı tutun (OpenCV: +X sağ, +Y aşağı, +Z ileri). Aşağı akış aracı OpenGL bekliyorsa (+Y yukarı) işaretleri değiştirin.
- Yoğun sahneler (> 1M nokta) için, bir alt örnekleme parametresi sunun; 500 MB'dan büyük PLY dosyaları her yerde yüklemek için hantaldır.
- "Makul" çıktı üretmek için derinliği asla sessizce kırpmayın; kullanıcıların neyin atıldığını bilmesi için uyarılmış eşiklerle açıkça kırpın.
