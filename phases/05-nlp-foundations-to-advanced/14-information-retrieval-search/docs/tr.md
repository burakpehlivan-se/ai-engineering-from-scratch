# Bilgi Getirme ve Arama

> BM25 kesindir ama kırılgandır. Dense geniş bir ağ atar ama anahtar kelimeleri kaçırır. Hibrit, 2026 varsayılanıdır. Geri kalanı optimizasyondur.

**Tür:** İnşa
**Diller:** Python
**Ön koşullar:** Faz 5 · 02 (BoW + TF-IDF), Faz 5 · 04 (GloVe, FastText, Subword)
**Süre:** ~75 dakika

## Problem

Bir kullanıcı "birisi para almak için yalan söylerse ne olur" diye yazar ve aslında bunu kapsayan yasal hükmü bulmayı bekler: "Ceza Kanunu Madde 420". Bir anahtar kelime araması bunu tamamen kaçırır (ortak kelime haznesi yok). Bir anlamsal arama, embedding'ler hukuki metin üzerinde eğitilmemişse bunu kaçırır. Gerçek arama her ikisini de ele almak zorundadır.

IR, her RAG sisteminin, her arama çubuğunun, her belge sitesinin bulanık aramasının altındaki pipeline'dır. 2026'da production'da çalışan mimari tek bir yöntem değildir. Birbirini tamamlayan bir yöntemler zinciridir, her biri bir öncekinin hatalarını yakalar.

Bu ders her bir parçayı inşa eder ve her birinin hangi hataları yakaladığını belirtir.

## Kavram

![Hybrid retrieval: BM25 + dense + RRF + cross-encoder rerank](../assets/retrieval.svg)

Dört katman. İhtiyacınız olanları seçin:

1. **Seyrek retrieval (BM25).** Hızlı, tam eşleşmelerde hassas, anlamsalarda berbat. Ters indeks üzerinde çalışır. Milyonlarca belge üzerinde sorgu başına 10ms'nin altında. Yasal referansları, ürün kodlarını, hata mesajlarını, adlı varlıkları doğru şekilde getirir.
2. **Yoğun retrieval (Dense retrieval).** Sorgu ve belgeleri vektörlere kodlar. En yakın komşu araması. Parafraselari ve anlamsal benzerliği yakalar. Bir karakter farklı olan tam anahtar kelime eşleştirmelerini kaçırır. FAISS veya vektör DB ile sorgu başına 50-200ms.
3. **Füzyon (Fusion).** Seyrek ve yoğun sıralı listeleri birleştirir. Reciprocal Rank Fusion (RRF), ham skorları (farklı ölçekte oldukları için) göz ardı edip yalnızca sıralama pozisyonlarını kullandığı için kolay bir varsayımdır. Ağırlıklı füzyon, bir sinyalin alanınızda baskın olduğunu bildiğinizde bir seçenektir.
4. **Cross-encoder rerank.** Füzyondan ilk 30'u alın. Bir cross-encoder çalıştırın (sorgu + belge birlikte, her çifti puanlayın). İlk 5'i saklayın. Cross-encoder'lar çift başına bi-encoder'lardan daha yavaştır ancak çok daha hassastır. Yalnızca ilk 30 üzerinde çalıştırarak amorti edersiniz.

Üçlü retrieval (BM25 + yoğun + SPLADE gibi learned-sparse), 2026 benchmark'larında ikiliyi geçer ancak learned-sparse indeksleri için altyapı gerektirir. Çoğu takım için iki artı cross-encoder rerank en iyi noktadır.

## İnşa Et

### Adım 1: sıfırdan BM25

```python
import math
import re
from collections import Counter

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text):
    return TOKEN_RE.findall(text.lower())


class BM25:
    def __init__(self, corpus, k1=1.5, b=0.75):
        if not corpus:
            raise ValueError("corpus must not be empty")
        self.corpus = [tokenize(d) for d in corpus]
        self.k1 = k1
        self.b = b
        self.n_docs = len(self.corpus)
        self.avg_dl = sum(len(d) for d in self.corpus) / self.n_docs
        self.df = Counter()
        for doc in self.corpus:
            for term in set(doc):
                self.df[term] += 1

    def idf(self, term):
        n = self.df.get(term, 0)
        return math.log(1 + (self.n_docs - n + 0.5) / (n + 0.5))

    def score(self, query, doc_idx):
        q_tokens = tokenize(query)
        doc = self.corpus[doc_idx]
        dl = len(doc)
        freq = Counter(doc)
        score = 0.0
        for term in q_tokens:
            f = freq.get(term, 0)
            if f == 0:
                continue
            numerator = f * (self.k1 + 1)
            denominator = f + self.k1 * (1 - self.b + self.b * dl / self.avg_dl)
            score += self.idf(term) * numerator / denominator
        return score

    def rank(self, query, top_k=10):
        scored = [(self.score(query, i), i) for i in range(self.n_docs)]
        scored.sort(reverse=True)
        return scored[:top_k]
```

#### Açıklama
Bu kod, Okapi BM25 algoritmasını sıfırdan uygular. `k1=1.5` terim sıklığı doygunluğunu kontrol eder; daha yüksek, terim tekrarına daha fazla ağırlık verir. `b=0.75` uzunluk normalleştirmesini kontrol eder; 0 belge uzunluğunu görmezden gelir, 1 tamamen normalleştirir. Varsayımlar orijinal makaleden Robertson'un önerileridir ve nadiren ayarlama gerektirir.

İki önemli parametre: `k1=1.5` terim sıklığı doygunluğunu kontrol eder; daha yüksek, terim tekrarına daha fazla ağırlık verir. `b=0.75` uzunluk normalleştirmesini kontrol eder; 0 belge uzunluğunu görmezden gelir, 1 tamamen normalleştirir. Varsayımlar orijinal makaleden Robertson'un önerileridir ve nadiren ayarlama gerektirir.

### Adım 2: bi-encoder ile yoğun retrieval

```python
from sentence_transformers import SentenceTransformer
import numpy as np


def build_dense_index(corpus, model_id="sentence-transformers/all-MiniLM-L6-v2"):
    encoder = SentenceTransformer(model_id)
    embeddings = encoder.encode(corpus, normalize_embeddings=True)
    return encoder, embeddings


def dense_search(encoder, embeddings, query, top_k=10):
    q_emb = encoder.encode([query], normalize_embeddings=True)
    sims = (embeddings @ q_emb.T).flatten()
    order = np.argsort(-sims)[:top_k]
    return [(float(sims[i]), int(i)) for i in order]
```

#### Açıklama
Embedding'leri L2-normalize edin ki çarpım cosinüse eşit olsun. `all-MiniLM-L6-v2` 384 boyutlu, hızlı ve çoğu İngilizce retrieval için yeterince güçlüdür. Çok dilli çalışmalar için `paraphrase-multilingual-MiniLM-L12-v2` kullanın. En yüksek hassasiyet için `bge-large-en-v1.5` veya `e5-large-v2`.

Embedding'leri L2-normalize edin ki çarpım cosinüse eşit olsun. `all-MiniLM-L6-v2` 384 boyutlu, hızlı ve çoğu İngilizce retrieval için yeterince güçlüdür. Çok dilli çalışmalar için `paraphrase-multilingual-MiniLM-L12-v2` kullanın.

### Adım 3: Reciprocal Rank Fusion

```python
def reciprocal_rank_fusion(rankings, k=60):
    scores = {}
    for ranking in rankings:
        for rank, (_, doc_idx) in enumerate(ranking):
            scores[doc_idx] = scores.get(doc_idx, 0.0) + 1.0 / (k + rank + 1)
    fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(score, doc_idx) for doc_idx, score in fused]
```

#### Açıklama
`k=60` sabiti orijinal RRF makalesinden gelmektedir. Daha yüksek `k`, sıralama farklarının katkısını düzleştirir; daha düşük `k`, üst sıralamaların baskın olmasını sağlar. 60, yayınlanmış varsayımdır ve nadiren ayarlama gerektirir.

`k=60` sabiti orijinal RRF makalesinden gelmektedir. Daha yüksek `k`, sıralama farklarının katkısını düzleştirir; daha düşük `k`, üst sıralamaların baskın olmasını sağlar. 60, yayınlanmış varsayımdır ve nadiren ayarlama gerektirir.

### Adım 4: hibrit arama + rerank

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def hybrid_search(query, bm25, encoder, dense_embeddings, corpus, top_k=5, pool_size=30, reranker=reranker):
    sparse_ranking = bm25.rank(query, top_k=pool_size)
    dense_ranking = dense_search(encoder, dense_embeddings, query, top_k=pool_size)
    fused = reciprocal_rank_fusion([sparse_ranking, dense_ranking])[:pool_size]

    pairs = [(query, corpus[doc_idx]) for _, doc_idx in fused]
    scores = reranker.predict(pairs)
    reranked = sorted(zip(scores, [doc_idx for _, doc_idx in fused]), reverse=True)
    return reranked[:top_k]
```

#### Açıklama
Üç aşama bir araya getirilmiştir. BM25 kelimsel eşleşmeleri bulur. Dense anlamsal eşleşmeleri bulur. RRF, iki sıralamayı skor kalibrasyonu gerekmeden birleştirir. Cross-encoder, sorgu-belge çiftlerini birlikte kullanarak ilk 30'u yeniden puanlar, bi-encoder'ın kaçırdığı ince ayrımı yakalar. İlk 5'i saklayın.

Üç aşama bir araya getirilmiştir. BM25 kelimsel eşleşmeleri bulur. Dense anlamsal eşleşmeleri bulur. RRF, iki sıralamayı skor kalibrasyonu gerekmeden birleştirir. Cross-encoder, sorgu-belge çiftlerini birlikte kullanarak ilk 30'u yeniden puanlar, bi-encoder'ın kaçırdığı ince ayrımı yakalar.

### Adım 5: değerlendirme

| Metrik | Anlamı |
|--------|---------|
| Recall@k | Doğru belgenin bulunduğu sorgularda, kaç kez en iyi `k`'da bulunuyor? |
| MRR (Mean Reciprocal Rank) | İlk ilgili belgenin 1/sıralamasının ortalaması. |
| nDCG@k | Yalnızca ikili ilgili/değil değil, ilgi gradyanlarını hesaba katar. |

Özellikle RAG için, retriever'ın **Recall@k**'ı en önemli sayıdır. Doğru paragraf getirilen sette yoksa reader cevaplayamaz.

Hata ayıklama ipucu: başarısız sorgular için seyrek ve yoğun sıralamaları karşılaştırın. Biri doğru belgeyi buluyor diğeri bulmuyorsa, kelime haznesi uyuşmazlığınız var (çözüm: eksik kısmı ekleyin) veya anlamsal belirsizlik (çözüm: daha iyi embedding'ler veya bir reranker).

## Kullan

2026 stacki:

| Ölçek | Stack |
|-------|-------|
| 1k-100k belge | Bellek içi BM25 + `all-MiniLM-L6-v2` embedding'leri + RRF. Ayrı DB yok. |
| 100k-10M belge | Dense için FAISS veya pgvector + BM25 için Elasticsearch / OpenSearch. Paralel çalıştırın. |
| 10M+ belge | Hibrit destekli Qdrant / Weaviate / Vespa / Milvus. İlk 30 üzerinde cross-encoder rerank. |
| En yüksek kalite sınırı | Üçlü (BM25 + dense + SPLADE) + ColBERT geç etkileşimli reranking |

Seçtiğiniz her ne olursa olsun, değerlendirme için bütçe ayırın. Retrieval recall'ını, uçtan uca RAG doğruluğunu benchmark etmeden önce benchmark edin. Reader, retriever'ın kaçırdığı şeyi düzeltemez.

### 2026 production RAG'tan zor kazanılan dersler

- **RAG hatalarının %80'i ingestion ve chunking'e kadar izlenir, modele değil.** Takımlar haftalarca LLM'leri değiştirir ve prompt'ları ayarlar, retrieval ise sessizce her üç sorguda bir yanlış bağlamı getirir. Önce chunking'i düzeltin.
- **Chunking stratejisi chunk boyutundan daha önemlidir.** Sabit boyutlu bölücüler tabloları, kodu ve iç içe başlıkları bozar. Cümle farkındalığı varsayımdır; anlamsal veya LLM tabanlı chunking teknik belgelerde ve ürün kılavuzlarında işe yarar.
- **Parent-doc kalıbı.** Hassasiyet için küçük "çocuk" parçacıkları getirin. Aynı ana bölümden birden fazla çocuk göründüğünde, bağlamı korumak için ana bloğu değiştirin. Bu, yeniden eğitimsiz cevap kalitesini tutarlı şekilde artırır.
- **k_rerank=3 genellikle optimaldir.** Bundan sonraki her ek parçacık, token maliyeti ve üretim gecikmesi ekler ancak cevap kalitesini artırmaz. Sizde hâlâ k=8, k=3'ten daha iyiyse, reranker yetersiz çalışıyor.
- **HyDE / query expansion.** Sorgudan hipotez bir cevap üretin, onu embed edin, getirin. Kısa sorular ve uzun belgeler arasındaki ifade farkını köprüler. Eğitim olmadan ücretsiz hassasiyet artışı.
- **Bağlam bütçesi 8K token altında.** O sınırdaki tutarlı isabetler, reranker eşiğinin çok gevşek olduğunu gösterir.
- **Her şeyi versiyonlayın.** Prompt'lar, chunking kuralları, embedding modeli, reranker. Herhangi bir kayma sessizce cevap kalitesini bozar. Sadakat, bağlam hassasiyeti ve cevapsız-soru oranı üzerinde CI kapıları, kullanıcılar görmeden önce gerilemeleri engeller.
- **Üçlü retrieval (BM25 + dense + SPLADE gibi learned-sparse), ikiliyi geçer** 2026 benchmark'larında, özellikle özel isimler ve anlamsalı karıştıran sorgularda. Altyapı SPLADE indekslerini desteklediğinde production'a çıkarın.

2026 endüstri ölçümlerine göre, doğru retrieval tasarımı halüsinasyonları %70-90 azaltır. Çoğu RAG performans kazanımı daha iyi retrieval'den gelir, model fine-tuning'inden değil.

## Ürün Olarak Kullan

`outputs/skill-retrieval-picker.md` olarak kaydedin:

```markdown
---
name: retrieval-picker
description: Pick a retrieval stack for a given corpus and query pattern.
version: 1.0.0
phase: 5
lesson: 14
tags: [nlp, retrieval, rag, search]
---

Given requirements (corpus size, query pattern, latency budget, quality bar, infra constraints), output:

1. Stack. BM25 only, dense only, hybrid (BM25 + dense + RRF), hybrid + cross-encoder rerank, or three-way (BM25 + dense + learned-sparse).
2. Dense encoder. Name the specific model. Match to language(s), domain, and context length.
3. Reranker. Name the specific cross-encoder model if used. Flag that rerank adds 30-100ms latency on top-30.
4. Evaluation plan. Recall@10 is the primary retriever metric. MRR for multi-answer. Baseline first, incremental improvements measured against it.

Refuse to recommend dense-only for corpora with named entities, error codes, or product SKUs unless the user has evidence dense handles exact matches. Refuse to skip reranking for high-stakes retrieval (legal, medical) where the final top-5 decides the user's answer.
```

#### Açıklama
Bu, gereksinimler verildiğinde retrieval stacki, dense encoder, reranker ve değerlendirme planı seçen bir skill tanımıdır.

## Alıştırmalar

1. **Kolay.** Yukarıdaki `hybrid_search`'i 500 belgelik bir corpus üzerinde uygulayın. 20 sorguyu test edin. Yalnızca BM25, yalnızca dense ve hibrit arasındaki recall@5'i karşılaştırın.
2. **Orta.** MRR hesaplaması ekleyin. Bilinen doğru belgeye sahip her test sorgusu için, doğru belgenin BM25, dense ve hibrit sıralamalarındaki sırasını bulun. Her biri için MRR'yi raporlayın.
3. **Zor.** MultipleNegativesRankingLoss (Sentence Transformers) kullanarak yoğun encoder'ı alanınız üzerinde fine-tune edin. 500 sorgu-belge çiftinden bir eğitim seti oluşturun. Fine-tuning öncesi ve sonrasında recall'ı karşılaştırın.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| BM25 | Anahtar kelime araması | Okapi BM25. Belgeleri terim sıklığı, IDF ve uzunluğa göre puanlar. |
| Dense retrieval | Vektör araması | Sorgu + belgeyi vektörlere kodlar, en yakın komşuları bulur. |
| Bi-encoder | Embedding modeli | Sorgu ve belgeyi bağımsız olarak kodlar. Sorgu zamanında hızlı. |
| Cross-encoder | Reranker modeli | Sorgu + belgeyi birlikte kodlar. Yavaş ama hassas. |
| RRF | Sıralama füzyonu | İki sıralamayı `1/(k + rank)` toplayarak birleştirir. |
| Recall@k | Retrieval metriği | İlgili bir belgenin en iyi `k`'da bulunduğu sorguların oranı. |

## İleri Okuma

- [Robertson ve Zaragoza (2009). The Probabilistic Relevance Framework: BM25 and Beyond](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf) — kesin BM25 incelemesi.
- [Karpukhin et al. (2020). Dense Passage Retrieval for Open-Domain QA](https://arxiv.org/abs/2004.04906) — DPR, klasik bi-encoder.
- [Formal et al. (2021). SPLADE: Sparse Lexical and Expansion Model](https://arxiv.org/abs/2107.05720) — dense ile farkı kapatan learned-sparse retriever.
- [Cormack, Clarke, Büttcher (2009). Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) — RRF makalesi.
- [Khattab ve Zaharia (2020). ColBERT: Efficient and Effective Passage Search](https://arxiv.org/abs/2004.12832) — geç etkileşimli retrieval.