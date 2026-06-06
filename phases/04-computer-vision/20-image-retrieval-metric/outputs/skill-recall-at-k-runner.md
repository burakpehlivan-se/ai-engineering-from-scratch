---
name: skill-recall-at-k-runner
description: Eğitim/val/galeri bölünmeleri ve uygun veri sözleşmesi ile recall@K için temiz bir değerlendirme koşum takımı yazın
version: 1.0.0
phase: 4
lesson: 20
tags: [erişim, değerlendirme, recall, faiss]
---

# Recall@K Koşucusu

Sorgu ve galeri görüntülerinin olduğu bir klasörü artı etiketleri tekrarlanabilir bir recall@K sayısına dönüştürün.

## Ne zaman kullanılır

- Yeni bir omurga için ilk erişim kıyaslaması.
- İnce ayar dönemleri boyunca gömme kalitesini izleme.
- Aynı veri kümesi üzerinde iki erişim sistemini karşılaştırma.

## Girdiler

- `query_images`: yol listesi.
- `gallery_images`: yol listesi (sorgu örtüşebilir veya örtüşmeyebilir).
- `query_labels`, `gallery_labels`: sınıf veya örnek kimlikleri.
- `encoder_fn`: çağrılabilir `image -> embedding` (önceden hesaplanmış veya canlı).
- `ks`: `[1, 5, 10]` gibi bir liste.

## Adımlar

1. Her galeri görüntüsünü bir kez kodlayın. Numpy dizisi olarak kaydedin.
2. Her sorgu görüntüsünü kodlayın.
3. Her iki gömme setini L2 normalleştirin.
4. Her sorgu için, tüm galeri öğelerine karşı benzerliği hesaplayın.
5. Azalan şekilde sıralayın, max(ks) üst alın.
6. Her K için, üst-K galeri öğelerinden herhangi birinin sorgunun etiketini paylaşıp paylaşmadığını kontrol edin.
7. `recall@K = üst K'da en az bir doğru komşusu olan sorguların oranı` raporlayın.

## Çıktı şablonu

```python
import numpy as np
from sklearn.preprocessing import normalize

def encode_all(images, encoder_fn, batch=32):
    out = []
    for i in range(0, len(images), batch):
        embs = encoder_fn(images[i:i + batch])
        out.append(embs)
    return np.concatenate(out)


def recall_at_k(query_emb, gallery_emb, q_labels, g_labels,
                ks=(1, 5, 10), query_ids=None, gallery_ids=None):
    if len(query_emb) == 0 or len(gallery_emb) == 0:
        return {f"recall@{k}": 0.0 for k in ks}

    g_label_set = set(g_labels.tolist())
    keep = np.array([lbl in g_label_set for lbl in q_labels])
    if not keep.any():
        return {f"recall@{k}": 0.0 for k in ks}

    q_emb_f = query_emb[keep]
    q_lab_f = q_labels[keep]
    q_id_f = query_ids[keep] if query_ids is not None else None

    q = normalize(q_emb_f)
    g = normalize(gallery_emb)
    sims = q @ g.T

    if q_id_f is not None and gallery_ids is not None:
        self_mask = q_id_f[:, None] == gallery_ids[None, :]
        sims = np.where(self_mask, -np.inf, sims)

    top_k_max = min(max(ks), g.shape[0])
    if top_k_max <= 0:
        return {f"recall@{k}": 0.0 for k in ks}

    top = np.argpartition(-sims, top_k_max - 1, axis=1)[:, :top_k_max]
    sorted_top = np.take_along_axis(
        top, np.argsort(-sims[np.arange(len(q))[:, None], top], axis=1), axis=1
    )
    out = {}
    for k in ks:
        k_eff = min(k, top_k_max)
        hits = np.any(g_labels[sorted_top[:, :k_eff]] == q_lab_f[:, None], axis=1)
        out[f"recall@{k}"] = float(hits.mean())
    return out


def evaluate(query_images, query_labels, gallery_images, gallery_labels, encoder_fn, ks=(1, 5, 10)):
    q_emb = encode_all(query_images, encoder_fn)
    g_emb = encode_all(gallery_images, encoder_fn)
    return recall_at_k(q_emb, g_emb, np.array(query_labels), np.array(gallery_labels), ks)
```

## Rapor

```
[evaluation]
  num queries:   <int>
  num gallery:   <int>
  embedding_dim: <int>

[recall]
  recall@1:  <float>
  recall@5:  <float>
  recall@10: <float>
```

## Kurallar

- Benzerliği hesaplamadan önce gömme'leri normalleştirin; normalleştirilmiş vektörler üzerinde FAISS IndexFlatIP kosinüse eşittir.
- Bir sorgunun temel doğruluk etiketi galeride yoksa, onu hariç tutun; aksi takdirde recall önemsiz şekilde 1'in altında sınırlanır.
- Sorgu ve galeri örtüşüyorsa, sorgunun kendisini kendi üst-K'sından hariç tutun, yoksa öz-benzerliği değil erişimi ölçersiniz.
- `num_queries > 10,000` için, OOM'dan kaçınmak amacıyla benzerlik matmul'unu toplu işleyin.
