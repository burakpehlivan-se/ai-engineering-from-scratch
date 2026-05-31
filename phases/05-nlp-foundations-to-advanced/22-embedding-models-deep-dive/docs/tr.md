# Embedding Modelleri — 2026 Derin Dalış

> Word2Vec her sözcük için bir vektör veriyordu. Modern embedding modelleri her parçacık için bir vektör verir, diller arası, seyrek (sparse), yoğun (dense) ve çoklu vektör görünümleriyle, indeksinize sığacak boyutta. Yanlış seçerseniz RAG yanlış şeyi getirir.

**Tür:** Öğren
**Diller:** Python
**Önkoşullar:** Faz 5 · 03 (Word2Vec), Faz 5 · 14 (Bilgi Getirme)
**Süre:** ~60 dakika

## Sorun

RAG sisteminiz yanlış parçacığı %40 oranında getiriyor. Suçlu nadiren vektör veritabanı veya prompt'tur. Suçlu embedding modelidir.

2026'da bir embedding seçmek beş eksende seçim yapmak demektir:

1. **Yoğun vs seyrek vs çoklu vektör.** Her parçacık için bir vektör, veya her token için bir vektör, veya seyrek ağırlıklı sözcük çantası.
2. **Dil kapsamı.** Tek dil İngilizce modeller hâlâ yalnızca İngilizce görevlerde kazanır. Çok dilli modeller karmaşık kümelerde kazanır.
3. **Bağlam uzunluğu.** 512 token vs 8.192 vs 32.768 — ve gerçek etkili kapasite genellikle reklam maksimumunun %60-70'idir.
4. **Boyut bütçesi.** Tam hassasiyette 3.072 float = vektör başına 12 KB. 100 milyon vektörde depolama $1.300/ay'dır. Matryoshka kırpma (truncation) bunu 4 kat azaltır.
5. **Açık vs barındırılan (hosted).** Açık ağırlık (open-weight) istack ve veri üzerinde kontrol sahibi olduğunuz anlamına gelir. Barındırılan ise kontrolü her zaman en güncel sürüme karşılık verirsiniz demektir.

Bu ders takasları (tradeoffs) isimlendirir ki kanıta dayalı seçim yapabilirsiniz, geçen季度 popüler olan herhangi bir şeye değil.

## Kavram

![Yoğun, seyrek ve çoklu vektör embeddingleri](../assets/embedding-modes.svg)

**Yoğun embeddingler.** Her parçacık için bir vektör (genellikle 384-3.072 boyut). Kosinüs benzerliği (cosine similarity), parçacıkları anlamsal yakınlığa göre sıralar. OpenAI `text-embedding-3-large`, BGE-M3 yoğun kipi, Voyage-3. Varsayılan seçim.

**Seyrek embeddingler.** SPLADE tarzı. Bir transformer, her sözcük hazinesi (vocab) token'ı için bir ağırlık tahmin eder, ardından çoğunun sıfırını alır. Sonuç |vocab| boyutunda seyrek bir vektördür. Sözcük eşleşmesini (lexical matching) yakalar (BM25 gibi) ancak öğrenilmiş terim ağırlıklarıyla. Anahtar sözcük ağırlıklı sorgularda güçlüdür.

**Çoklu vektör (geç etkileşim - late interaction).** ColBERTv2, Jina-ColBERT. Her token için bir vektör. MaxSim ile puanlama: her sorgu token'ı için en benzer belge token'ını bulun, puanları toplayın. Depolama ve puanlama açısından daha pahalıdır, ancak uzun sorgularda ve alana özgü kümelerde kazanır.

**BGE-M3: üçünü birden.** Tek bir model yoğun, seyrek ve çoklu vektör temsillerini aynı anda üretir. Her biri bağımsız olarak sorgulanabilir; puanlar ağırlıklı toplamla birleşir. Tek bir checkpoint'tan esneklik istiyorsanız 2026 varsayılanı budur.

**Matryoshka Temsil Öğrenmesi (Representation Learning).** Vektörün ilk N boyutunun tek başına faydalı bir embedding oluşturacak şekilde eğitilmesi. 1.536 boyutlu bir vektörü 256'ya kırpın ve ~%1 doğruluk kaybıyla 6 kat depolama tasarrufu yapın. OpenAI text-3, Cohere v4, Voyage-4, Jina v5, Gemini Embedding 2, Nomic v1.5+ tarafından desteklenir.

### MTEB liderlik tablosu kısmi bir hikaye anlatır

Massive Text Embedding Benchmark — lansmanda (2022) 8 görev türünde 56 görev, MTEB v2'de 100+ göreve genişletildi. 2026 başında Gemini Embedding 2retrieve'yi zirveye taşır (67.71 MTEB-R). Cohere embed-v4 genel sıralamada öndedir (65.2 MTEB). BGE-M3 açık ağırlıklı çok dilli sıralamada öndedir (63.0). Liderlik tablosu gerekli ama yeterli değil — her zaman kendi alanınızda benchmark çalıştırın.

### Üç katmanlı model

| Kullanım durumu | Model |
|----------|---------|
| Hızlı ilk tarama | Yoğun bi-encoder (BGE-M3, text-3-small) |
| Hatırlama artışı | Seyrek (SPLADE, BGE-M3 sparse) + RRF birleştirme |
| İlk 50'de hassasiyet | Çoklu vektör (ColBERTv2) veya çapraz encoder (cross-encoder) yeniden sıralama |

Çoğu üretim yığını üçünü de kullanır.

## İnşa Et

### Adım 1: temel — Sentence-BERT ile yoğun embeddingler

```python
from sentence_transformers import SentenceTransformer
import numpy as np

encoder = SentenceTransformer("BAAI/bge-small-en-v1.5")
corpus = [
    "The first iPhone launched in 2007.",
    "Apple released the iPod in 2001.",
    "Android is an operating system from Google.",
]
emb = encoder.encode(corpus, normalize_embeddings=True)

query = "When was the iPhone released?"
q_emb = encoder.encode([query], normalize_embeddings=True)[0]
scores = emb @ q_emb
print(sorted(enumerate(scores), key=lambda x: -x[1]))
```

#### Açıklama
Bu kod, Sentence-BERT modelini kullanarak bir corpus üzerinde yoğun embeddingler üretir ve bir sorgu ile kosinüs benzerliğini hesaplar. `normalize_embeddings=True`, nokta çarpımının kosinüs benzerliğine eşit olmasını sağlar.

`normalize_embeddings=True` seçeneği nokta çarpımını kosinüs benzerliğine eşit kılar. Her zaman ayarlayın.

### Adım 2: Matryoshka kırpma

```python
def truncate(vectors, dim):
    out = vectors[:, :dim]
    return out / np.linalg.norm(out, axis=1, keepdims=True)

emb_256 = truncate(emb, 256)
emb_128 = truncate(emb, 128)
```

#### Açıklama
Bu fonksiyon, embedding vektörlerini daha düşük bir boyuta kırpıp yeniden normalizer. Matryoshka ile eğitilmiş modeller için ilk birkaç düzeyde kayıpsızdır.

Kırpma sonrası yeniden normalizasyon yapın. Nomic v1.5, OpenAI text-3 ve Voyage-4, bunun ilk birkaç düzeyde kayıpsız olacak şekilde eğitilmiştir. Matryoshka olmayan modeller (orijinal Sentence-BERT) kırpıldığında keskin düşüş gösterir.

### Adım 3: BGE-M3 çok işlevlilik

```python
from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)

output = model.encode(
    corpus,
    return_dense=True,
    return_sparse=True,
    return_colbert_vecs=True,
)
# output["dense_vecs"]:    (n_docs, 1024)
# output["lexical_weights"]: list of dict {token_id: weight}
# output["colbert_vecs"]:  list of (n_tokens, 1024) arrays
```

#### Açıklama
Bu kod, BGE-M3 modelini kullanarak aynı anda yoğun, seyrek ve çoklu vektör temsilleri üretir. Üç farklı indeks türü tek bir çıkarım çağrısıyla elde edilir.

Üç indeks, tek bir çıkarım çağrısı. Puan birleştirme (score fusion):

```python
dense_score = ... # cosine over dense_vecs
sparse_score = model.compute_lexical_matching_score(q_lex, d_lex)
colbert_score = model.colbert_score(q_col, d_col)
final = 0.4 * dense_score + 0.2 * sparse_score + 0.4 * colbert_score
```

#### Açıklama
Bu kod, üç farklı embedding türünün puanlarını ağırlıklı olarak birleştirir. Ağırlıkları kendi alanınızda ayarlayın.

Ağırlıkları kendi alanınızda ayarlayın.

### Adım 4: özel görev üzerinde MTEB değerlendirmesi

```python
from mteb import MTEB

tasks = ["ArguAna", "SciFact", "NFCorpus"]
evaluation = MTEB(tasks=tasks)
results = evaluation.run(encoder, output_folder="./mteb-results")
```

#### Açıklama
Bu kod, aday modellerinizi MTEB benchmark'ı üzerinde çalıştırır. Temsili bir alt küme kullanın — yalnızca liderlik tablosu sıralamasına güvenmeyin.

Aday modellerinizi *temsili* bir alt küme üzerinde çalıştırın. Yalnızca liderlik tablosu sıralamasına güvenmeyin — alanınız önemlidir.

### Adım 5: sıfırdan el yapımı kosinüs

`code/main.py` dosyasına bakın. Ortalama Hashing Trick embeddingleri (yalnızca stdlib). Transformer embeddingleriyle rekabet edemez, ancak biçimi gösterir: tokenizasyon → vektör → normalizasyon → nokta çarpımı.

## Tuzaklar

- **Sorgu ve belge için aynı model.** Bazı modeller (Voyage, Jina-ColBERT) asimetrik kodlama kullanır — sorgu ve belge farklı yollardan geçer. Her zaman model kartına bakın.
- **Eksik önek (prefix).** `bge-*` modelleri sorgulara `"Represent this sentence for searching relevant passages: "` eklenmesini gerektirir. Unutursanız 3-5 puan hatırlama farkı olur.
- **Aşırı kırpılmış Matryoshka.** 1.536 → 256 genellikle güvenlidir. 1.536 → 64 değildir. Değerlendirme kümenizde doğrulayın.
- **Bağlam kırpılması.** Çoğu model maksat uzunluğunu aşan girdileri sessizce kırpar. Uzun belgeler için parçalama (chunking) gerekir (ders 23'e bakın).
- **Gecikme kuyruğunu görmezden gelme.** MTEB puanları p99 gecikmesini gizler. 600M'lik bir model 335M'lik modeli 2 puan geçebilir ancak sorgu başına 3 kat daha pahalıya mal olabilir.

## Kullan

2026 yığını:

| Durum | Seçin |
|-----------|------|
| Yalnızca İngilizce, hızlı, API | `text-embedding-3-large` veya `voyage-3-large` |
| Açık ağırlıklı, İngilizce | `BAAI/bge-large-en-v1.5` |
| Açık ağırlıklı, çok dilli | `BAAI/bge-m3` veya `Qwen3-Embedding-8B` |
| Uzun bağlam (32k+) | Voyage-3-large, Cohere embed-v4, Qwen3-Embedding-8B |
| Yalnızca CPU konuşlandırma | Nomic Embed v2 (137M parametre, MoE) |
| Depolama kısıtlı | Matryoshka kırpılmış + int8 kuantizasyon |
| Anahtar sözcük ağırlıklı sorgular | SPLADE seyrek ekleyin, yoğun ile RRF birleştirin |

2026 modeli: BGE-M3 veya text-3-large ile başlayın, MTEB ile kendi alanınızda değerlendirin, alana özgü bir model 3 puandan fazla kazanıyorsa değiştirin.

## Teslim Et

`outputs/skill-embedding-picker.md` olarak kaydedin:

```markdown
---
name: embedding-picker
description: Pick embedding model, dimension, and retrieval mode for a given corpus and deployment.
version: 1.0.0
phase: 5
lesson: 22
tags: [nlp, embeddings, retrieval]
---

Given a corpus (size, languages, domain, avg length), deployment target (cloud / edge / on-prem), latency budget, and storage budget, output:

1. Model. Named checkpoint or API. One-sentence reason.
2. Dimension. Full / Matryoshka-truncated / int8-quantized. Reason tied to storage budget.
3. Mode. Dense / sparse / multi-vector / hybrid. Reason.
4. Query prefix / template if required by the model card.
5. Evaluation plan. MTEB tasks relevant to domain + held-out domain eval with nDCG@10.

Refuse recommendations that truncate Matryoshka to <64 dims without domain validation. Refuse ColBERTv2 for corpora under 10k passages (overhead not justified). Flag long-document corpora (>8k tokens) routed to models with 512-token windows.
```

#### Açıklama
Bu şablon, bir corpus ve konuşlandırma hedefi için embedding modeli, boyut ve getirme modunu seçen bir yetenek tanımıdır.

## Alıştırmalar

1. **Kolay.** 100 cümleyi `bge-small-en-v1.5` ile tam boyutta (384) kodlayın, ardından Matryoshka 128'de kodlayın. 10 sorgu üzerinde MRR düşüşünü ölçün.
2. **Orta.** BGE-M3 yoğun, seyrek ve colbert seçeneklerini kendi alanınızdan 500 parçacık üzerinde karşılaştırın. recall@10'da hangisi kazanır? RRF birleştirme en iyi tek kipten daha iyi mi?
3. **Zor.** En iki 2 alan görevinizde üç aday model üzerinde MTEB çalıştırın. MTEB puanını, 100 sorguluk bir batch'te p99 gecikmesini ve $/1M sorgu değerini raporlayın. Pareto-optimal olanı seçin.

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Yoğun embedding (Dense embedding) | Vektör | Metin başına sabit boyutlu bir vektör. Sıralama için kosinüs benzerliği. |
| Seyrek embedding (Sparse embedding) | Öğrenilmiş BM25 | Sözcük hazinesi token'ı başına bir ağırlık; çoğunlukla sıfır; uçtan uca eğitilmiş. |
| Çoklu vektör (Multi-vector) | ColBERT tarzı | Token başına bir vektör; MaxSim puanlama; daha büyük indeks, daha iyi hatırlama. |
| Matryoshka | Rus bebek hilesi | İlk N boyut, tek başına geçerli daha küçük bir embedding oluşturur. |
| MTEB | Benchmark | Massive Text Embedding Benchmark — lansmanda 56 görev, v2'de 100+. |
| BEIR | Getirme benchmark'ı | 18 sıfır atıflı getirme görevi; genellikle çapraz alan dayanıklılığı için referans verilir. |
| Asimetrik kodlama (Asymmetric encoding) | Sorgu ≠ belge yolu | Model sorgular ve belgeler için farklı projeksiyonlar kullanır. |

## İleri Okuma

- [Reimers, Gurevych (2019). Sentence-BERT](https://arxiv.org/abs/1908.10084) — bi-encoder makalesi.
- [Muennighoff vd. (2022). MTEB: Massive Text Embedding Benchmark](https://arxiv.org/abs/2210.07316) — liderlik tablosu makalesi.
- [Chen vd. (2024). BGE-M3: Multi-lingual, Multi-functionality, Multi-granularity](https://arxiv.org/abs/2402.03216) — birleşik üç kipli model.
- [Kusupati vd. (2022). Matryoshka Representation Learning](https://arxiv.org/abs/2205.13147) — boyut merdiveni eğitim hedefi.
- [Santhanam vd. (2022). ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction](https://arxiv.org/abs/2112.01488) — üretimde geç etkileşim.
- [Hugging Face MTEB liderlik tablosu](https://huggingface.co/spaces/mteb/leaderboard) — canlı sıralamalar.