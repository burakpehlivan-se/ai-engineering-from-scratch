---
name: skill-image-text-retriever
description: Herhangi bir CLIP kontrol noktası ile bir görüntü gömme dizini oluşturun; metinle ve görüntüyle sorguyu destekleyin
version: 1.0.0
phase: 4
lesson: 18
tags: [clip, erişim, faiss, sıfır-atış]
---

# Görüntü-Metin Erişimcisi

CLIP gömme'lerini kullanarak bir klasörü görüntüleri aranabilir bir dizine dönüştürün.

## Ne zaman kullanılır

- Dahili bir katalog üzerinde sıfır atış görüntü arama inşa ederken.
- Neredeyse özdeş görüntüleri gömme uzaklığı ile tekilleştirirken.
- Etiketli veri kümesi olmadan hızlı bir "benzerini bul" bileşeni inşa ederken.

## Girdiler

- `image_folder`: görüntü dosyalarının dizini.
- `clip_model`: `openai/clip-vit-base-patch32` veya `google/siglip-base-patch16-224` gibi bir HuggingFace kimliği.
- `index_type`: flat | IVF | HNSW.
- `embedding_dim`: modelden çıkarılır.

## Adımlar

1. CLIP modelini ve ön işlemcisini yükleyin.
2. Klasördeki her görüntüyü toplu olarak kodlayın. Gömme'leri (N, D) float32 + dosya adı listesi olarak kaydedin.
3. Gömme'ler üzerinde bir FAISS dizini oluşturun. Kosinüs benzerliği için L2 normalleştirilmiş vektörler üzerinde iç çarpım kullanın.
4. İki sorgu arayüzü sunun:
   - `search_by_text(text, k)` — metni gömün, arayın.
   - `search_by_image(image_path, k)` — görüntüyü gömün, arayın.

## Çıktı şablonu

```python
import os
import glob
import numpy as np
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor
import faiss


class ImageTextRetriever:
    def __init__(self, model_name="openai/clip-vit-base-patch32"):
        self.model = CLIPModel.from_pretrained(model_name).eval()
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.dim = self.model.config.projection_dim
        self.index = None
        self.filenames = []

    @torch.no_grad()
    def _encode_images(self, paths, batch=16):
        embs = []
        for i in range(0, len(paths), batch):
            imgs = [Image.open(p).convert("RGB") for p in paths[i:i + batch]]
            inputs = self.processor(images=imgs, return_tensors="pt")
            out = self.model.get_image_features(**inputs)
            out = out / out.norm(dim=-1, keepdim=True)
            embs.append(out.cpu().numpy())
        return np.concatenate(embs).astype(np.float32)

    @torch.no_grad()
    def _encode_text(self, texts):
        inputs = self.processor(text=texts, return_tensors="pt", padding=True)
        out = self.model.get_text_features(**inputs)
        out = out / out.norm(dim=-1, keepdim=True)
        return out.cpu().numpy().astype(np.float32)

    def build_index(self, folder, index_type="flat"):
        exts = ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp")
        files = []
        for ext in exts:
            files.extend(glob.glob(os.path.join(folder, ext)))
        self.filenames = sorted(files)
        embs = self._encode_images(self.filenames)
        if index_type == "IVF":
            quantizer = faiss.IndexFlatIP(self.dim)
            nlist = min(256, max(4, len(embs) // 32))
            self.index = faiss.IndexIVFFlat(quantizer, self.dim, nlist)
            self.index.train(embs)
        elif index_type == "HNSW":
            self.index = faiss.IndexHNSWFlat(self.dim, 32, faiss.METRIC_INNER_PRODUCT)
        else:
            self.index = faiss.IndexFlatIP(self.dim)
        self.index.add(embs)

    def search_by_text(self, text, k=5):
        q = self._encode_text([text])
        dist, idx = self.index.search(q, k)
        return [(self.filenames[i], float(d)) for d, i in zip(dist[0], idx[0])]

    def search_by_image(self, image_path, k=5):
        q = self._encode_images([image_path])
        dist, idx = self.index.search(q, k)
        return [(self.filenames[i], float(d)) for d, i in zip(dist[0], idx[0])]
```

## Rapor

```
[retriever]
  model:          <isim>
  num_images:     <int>
  dim:            <int>
  index_type:     flat | IVF | HNSW
  index_size_mb:  <float>
```

## Kurallar

- Dizinlemeden önce her zaman gömme'leri L2 normalleştirin; normalleştirilmiş vektörler üzerinde FAISS'in iç çarpımı kosinüs benzerliğine eşittir.
- 100k'dan az görüntü için, `IndexFlatIP` (tam) en basit ve en hızlısıdır.
- 100k-10M için, `IndexIVFFlat` standart takastır.
- > 10M için, HNSW veya ürün-kantize bir varyant kullanın.
- Her sorguda dizini asla yeniden inşa etmeyin; bir kez gömün, birçok kez arayın.
