---
name: skill-linear-probe-runner
description: Herhangi bir dondurulmuş kodlayıcı ve etiketli veri kümesi için eksiksiz doğrusal proba değerlendirmesi yazın
version: 1.0.0
phase: 4
lesson: 17
tags: [kendi-kendine-denetimli, değerlendirme, doğrusal-proba, pytorch]
---

# Doğrusal Proba Koşucusu

Dondurulmuş bir kodlayıcının özelliklerini üstüne tek bir doğrusal sınıflandırıcı eğiterek değerlendirin. Her kendi kendine denetimli makale için standart değerlendirme.

## Ne zaman kullanılır

- Kendi kendine denetimli kontrol noktalarını karşılaştırırken.
- Ön eğitim dönemleri boyunca özellik kalitesini izlerken.
- İnce ayar yapmadan, önceden eğitilmiş bir kodlayıcının aşağı akış görevi için yeterince iyi olup olmadığına karar verirken.

## Girdiler

- `encoder`: görüntü başına sabit boyutlu özellik döndüren dondurulmuş `nn. Module`.
- `feature_dim`: kodlayıcı çıktısının boyutsallığı.
- `train_dataset`: etiketli veri kümesi (görüntü, sınıf_kimliği).
- `val_dataset`: tutulan set.
- `num_classes`: görev sınıfları.
- `epochs`: tipik olarak ImageNet ölçeği için 100, daha küçük veri kümeleri için 50.

## Adımlar

1. Kodlayıcıyı eval moduna ayarlayın ve her parametrede `requires_grad=False` yapın.
2. Hem eğitim hem val setleri için özellik çıkarımını bir kez yapın. Numpy dizileri veya bellek eşlemeli dosya olarak saklayın.
3. Önbelleğe alınmış özellikler üzerinde SGD + kosinüs çizelgesi ile `nn. Linear(feature_dim, num_classes)` eğitin.
4. Standart hiperparametreler: `lr=0.1`, `momentum=0.9`, `weight_decay=0`, `batch_size=1024`. Doğrusal proba `lr`'ye şaşırtıcı derecede duyarlıdır — doğruluk düşükse tarama yapın.
5. Eğitim sonunda val üzerinde top-1 doğruluğunu raporlayın.

## Çıktı şablonu

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torch.optim import SGD
from torch.optim.lr_scheduler import CosineAnnealingLR

def extract(encoder, loader, device="cpu"):
 encoder.eval()
 feats, labels = [], []
 with torch.no_grad():
 for x, y in loader:
 f = encoder(x.to(device)).cpu()
 feats.append(f)
 labels.append(y)
 return torch.cat(feats), torch.cat(labels)


def linear_probe(encoder, feature_dim, train_loader, val_loader,
 num_classes, epochs=50, lr=0.1, device="cpu"):
 for p in encoder.parameters():
 p.requires_grad = False

 f_train, y_train = extract(encoder, train_loader, device)
 f_val, y_val = extract(encoder, val_loader, device)

 head = nn. Linear(feature_dim, num_classes).to(device)
 opt = SGD(head.parameters(), lr=lr, momentum=0.9, weight_decay=0)
 sched = CosineAnnealingLR(opt, T_max=epochs)

 ds = torch.utils.data. TensorDataset(f_train, y_train)
 train_iter = DataLoader(ds, batch_size=1024, shuffle=True)

 best_val = 0.0
 for ep in range(epochs):
 head.train()
 for x, y in train_iter:
 x, y = x.to(device), y
 loss = F.cross_entropy(head(x), y)
 opt.zero_grad(); loss.backward(); opt.step()
 sched.step()

 head.eval()
 with torch.no_grad():
 acc = (head(f_val.to(device)).argmax(-1).cpu() == y_val).float().mean().item()
 best_val = max(best_val, acc)
 return best_val
```

## Rapor

```
[linear probe]
 encoder: <isim + ön eğitim kontrol noktası>
 feature_dim: <int>
 epochs: <int>
 best_val_top1: <float>
```

## Kurallar

- Doğrusal proba sırasında kodlayıcı ağırlıklarını asla güncellemeyin; bu bir ince ayar olurdu, proba değil.
- Özellikleri bir kez önceden hesaplayın; her dönemde kodlayıcıyı yeniden eğitmek 100x hesaplama israf eder.
- SGD'yi kosinüs çizelgesi ve ağırlık azalması olmadan kullanın; Adam bazen burada düşük performans gösterir.
- En az her kodlayıcı ailesi için öğrenme hızlarını tarayın; en uygun SSL yöntemleri arasında değişir.
