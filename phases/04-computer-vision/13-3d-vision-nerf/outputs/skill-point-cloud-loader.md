---
name: skill-point-cloud-loader
description: Doğru normalleştirme, merkezleme ve nokta örnekleme ile .ply / .pcd / .xyz dosyaları için bir PyTorch Veri Kümesi yazın
version: 1.0.0
phase: 4
lesson: 13
tags: [3d-görü, nokta-bulutu, veri-yükleme, pytorch]
---

# Nokta Bulutu Yükleyici

3B tarama dosyalarıyla dolu bir klasörü, eğitime hazır bir PyTorch `Dataset`'ine dönüştürün.

## Ne zaman kullanılır

- Yeni bir nokta bulutu sınıflandırma / bölümleme projesi başlatırken.
- `.ply`, `.pcd` ve `.xyz` formatları arasında geçiş yaparken.
- Hatasız eğiten ancak zayıf yakınsayan bir modeli ayıklarken; genellikle veri yükleyici normalleştirmesi yanlıştır.

## Girdiler

- `data_root`: nokta bulutu dosyalarının ve isteğe bağlı bir etiket CSV'sinin bulunduğu klasör.
- `file_format`: ply | pcd | xyz | npy.
- `num_points`: sabit örnekleme boyutu, tipik olarak 1024 veya 2048.
- `augmentation`: none | rotate | jitter | mixup.

## Normalleştirme politikası

Her üretim nokta bulutu hattı sırayla şunu uygular:

1. Bulutu **merkezle**: merkez noktayı (centroid) çıkar.
2. Birim küreye **ölçekle**: merkezden maksimum mesafeye böl.
3. `num_points` noktası **örnekle**. Bulut daha fazla noktaya sahipse, sadık şekil temsili için **en uzak nokta örneklemesi (FPS)** veya hız için rastgele örnekleme kullanın. Daha azsa, noktaları tekrarlayın.
4. Nokta sırasını **karıştır** (sıra zaten model için önemli olmamalı, ancak karıştırma yanlışlıkla sıra bağımlılıklarını kırar).

## Çıktı şablonu

```python
import numpy as np
import torch
from torch.utils.data import Dataset

try:
 import open3d as o3d
 HAS_O3D = True
except ImportError:
 HAS_O3D = False

def _read_ply(path):
 if HAS_O3D:
 pc = o3d.io.read_point_cloud(path)
 return np.asarray(pc.points, dtype=np.float32)
 # Geri dönüş: minimal ascii-ply okuyucu
 ...

def _fps(points, k):
 idx = np.zeros(k, dtype=np.int64)
 dist = np.full(len(points), np.inf)
 seed = np.random.randint(len(points))
 idx[0] = seed
 for i in range(1, k):
 dist = np.minimum(dist, ((points - points[idx[i-1]]) ** 2).sum(axis=1))
 idx[i] = int(np.argmax(dist))
 return idx

def normalise(points):
 centre = points.mean(axis=0)
 points = points - centre
 scale = np.max(np.linalg.norm(points, axis=1))
 return points / max(scale, 1e-8)

class PointCloudDataset(Dataset):
 def __init__(self, files, labels, num_points=1024, augment=False):
 self.files = files
 self.labels = labels
 self.num_points = num_points
 self.augment = augment

 def __len__(self):
 return len(self.files)

 def __getitem__(self, i):
 pts = _read_ply(self.files[i])
 pts = normalise(pts)
 if len(pts) >= self.num_points:
 idx = _fps(pts, self.num_points)
 pts = pts[idx]
 else:
 reps = int(np.ceil(self.num_points / len(pts)))
 pts = np.tile(pts, (reps, 1))[:self.num_points]
 # Yanlışlıkla bağımlılıkları kırmak için nokta sırasını karıştır
 # (özellikle belirleyici sırada noktaları döşerken önemli).
 np.random.shuffle(pts)
 if self.augment:
 theta = np.random.uniform(0, 2 * np.pi)
 R = np.array([[np.cos(theta), 0, np.sin(theta)],
 [0, 1, 0],
 [-np.sin(theta), 0, np.cos(theta)]], dtype=np.float32)
 pts = pts @ R
 pts = pts + np.random.normal(0, 0.02, pts.shape).astype(np.float32)
 pts = np.ascontiguousarray(pts, dtype=np.float32)
 return torch.from_numpy(pts).transpose(0, 1), int(self.labels[i])
```

## Rapor

```
[dataset]
 files: <N>
 format: <ply|pcd|xyz|npy>
 points_per_sample: <int>
 normalise: centre + unit sphere
 sampling: FPS | random
 augmentation: <list>
```

## Kurallar

- Ölçeklemeden önce her zaman merkezle; sırayı değiştirmek "birim küre"nin anlamını değiştirir.
- Şekil görevleri için rastgele örnekleme yerine FPS'i tercih edin; her noktanın zaten önemli olduğu segmentasyon için rastgele uygundur.
- Değerlendirme sırasında asla veri artırma yapmayın; yalnızca eğitim sırasında.
- Nokta bulutu dosyaları ekstra kanal olarak renk veya normaller içeriyorsa, Veri Kümesini yalnızca xyz yerine bir `(3 + C, num_points)` tensörü döndürecek şekilde genişletin.
