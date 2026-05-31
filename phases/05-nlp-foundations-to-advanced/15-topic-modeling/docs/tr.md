# Konu Modelleme — LDA ve BERTopic

> LDA: belgeler konuların karışımlarıdır, konular ise kelimeler üzerine dağılımlardır. BERTopic: belgeler embedding uzayında kümelere ayrılır, kümeler konulardır. Aynı hedef, farklı ayrıştırmalar.

**Tür:** Öğren
**Diller:** Python
**Ön koşullar:** Faz 5 · 02 (BoW + TF-IDF), Faz 5 · 03 (Word2Vec)
**Süre:** ~45 dakika

## Problem

10.000 müşteri destek talebiniz, 50.000 haber makaleniz veya 200.000 tweet'iniz var. Topluluğun ne hakkında olduğunu okumadan bilmeniz gerekiyor. Etiketli kategorileriniz yok. Kaç kategori olduğunu bile bilmiyorsunuz.

Konu modelleme bunu denetimsiz olarak cevaplar. Bir corpus verin, tutarlı bir konu kümesi ve her belge için bu konular üzerine bir dağılım elde edin.

İki algoritma ailesi baskındır. LDA (2003), her belgeyi gizli konuların bir karışımı, her konuyu ise kelimeler üzerine bir dağılım olarak ele alır. Çıkarım Bayesian'dir. Karışık üyelik konu atamaları ve açıklanabilir kelime düzeyinde olasılık dağılımları gerektiğinde production'da hâlâ kullanılır.

BERTopic (2020), belgeleri BERT ile kodlar, UMAP ile boyut düşürür, HDBSCAN ile kümeleme yapar ve sınıf-tabanlı TF-IDF ile konu kelimelerini çıkarır. Kısa metin, sosyal medya ve anlamsal benzerliğin kelime örtüşmesinden daha önemli olduğu her alanda kazanır. Bir belge bir konu alır, bu da uzun biçimli içerik için bir kısıtlamadır.

Bu ders her ikisi için sezgi geliştirir ve bir corpus için hangisinin seçileceğini belirtir.

## Kavram

![LDA mixture model vs BERTopic clustering](../assets/topic-modeling.svg)

**LDA üretici hikayesi.** Her konu kelimeler üzerine bir dağılımdır. Her belge konuların bir karışımıdır. Bir belgede bir kelime üretmek için, belgenin karışımından bir konu örnekle (sample), sonra o konunun dağılımından bir kelime örnekle. Çıkarım bunu tersine çevirir: gözlemlenen kelimeler verildiğinde, belge başına konu dağılımını ve konu başına kelime dağılımını çıkarır. Çökmüş Gibbs örnekleme (Collapsed Gibbs sampling) veya değişken Bayes (variational Bayes) matematiği yapar.

Temel LDA çıktısı:

- `doc_topic`: `(n_docs, n_topics)` matrisi, her satır 1'e eşittir (belgenin konu karışımı).
- `topic_word`: `(n_topics, vocab_size)` matrisi, her satır 1'e eşittir (konunun kelime dağılımı).

**BERTopic pipeline'ı.**

1. Her belgeyi bir cümle transformer'ı ile kodlayın (örn. `all-MiniLM-L6-v2`). 384 boyutlu vektörler.
2. UMAP ile boyutu ~5'e düşürün. BERT embedding'leri kümeleme için çok boyutludur.
3. HDBSCAN ile kümeleme yapın. Yoğunluk tabanlı, değişken boyutlu kümeler ve "aykırı" etiketi üretir.
4. Her küme için, kümenin belgeleri üzerinde sınıf-tabanlı TF-IDF hesaplayarak üst kelimeleri çıkarın.

Çıktı, belge başına bir konu (artı -1 aykırı etiketi) şeklindedir. İsteğe bağlı olarak, HDBSCAN'in olasılık vektörü aracılığıyla yumuşak üyelik.

## İnşa Et

### Adım 1: scikit-learn ile LDA

```python
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np


def fit_lda(documents, n_topics=5, max_features=1000):
    cv = CountVectorizer(
        max_features=max_features,
        stop_words="english",
        min_df=2,
        max_df=0.9,
    )
    X = cv.fit_transform(documents)
    lda = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        max_iter=50,
        learning_method="online",
    )
    doc_topic = lda.fit_transform(X)
    feature_names = cv.get_feature_names_out()
    return lda, cv, doc_topic, feature_names


def print_top_words(lda, feature_names, n_top=10):
    for idx, topic in enumerate(lda.components_):
        top_idx = np.argsort(-topic)[:n_top]
        words = [feature_names[i] for i in top_idx]
        print(f"topic {idx}: {' '.join(words)}")
```

#### Açıklama
Dikkat edin: durak kelimeler kaldırılmış, min_df ve max_df nadir ve her yerde bulunan terimleri filtreler, CountVectorizer (TfidfVectorizer değil) çünkü LDA ham sayılara ihtiyaç duyar.

### Adım 2: BERTopic (production)

```python
from bertopic import BERTopic

topic_model = BERTopic(
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    min_topic_size=15,
    verbose=True,
)

topics, probs = topic_model.fit_transform(documents)
info = topic_model.get_topic_info()
print(info.head(20))
valid_topics = info[info["Topic"] != -1]["Topic"].tolist()
for topic_id in valid_topics[:5]:
    print(f"topic {topic_id}: {topic_model.get_topic(topic_id)[:10]}")
```

#### Açıklama
`Topic != -1` filtresi, BERTopic'in aykırı (outlier) bucket'ını (HDBSCAN'in kümeleyemediği belgeleri) düşürür. `min_topic_size`, HDBSCAN'in minimum küme boyutunu kontrol eder; BERTopic'in kütüphane varsayılanı 10'dur. Bu örnek, dersin ölçeği için açıkça 15'e ayarlar. 10.000'den fazla belgelik corpus'larda 50 veya 100'e çıkarın.

### Adım 3: değerlendirme

Her iki yöntem de konu kelimeleri üretir. Soru, bu kelimelerin tutarlı olup olmadığıdır:

- **Konu tutarlılığı (c_v).** Üst kelime çiftlerinin kayan pencere bağlamındaki NPMI'sini (normalized pointwise mutual information) birleştirir, skorları konu vektörlerine toplar ve bu vektörleri cosinüs benzerliği ile karşılaştırır. Daha yükseği daha iyidir. `gensim.models.CoherenceModel` ile `coherence="c_v"` kullanın.
- **Konu çeşitliliği.** Tüm konuların üst kelimeleri arasındaki benzersiz kelimelerin oranı. Daha yükseği daha iyidir (konular çakışmaz).
- **Nitel inceleme.** Her konunun üst kelimelerini okuyun. Gerçek bir şeyi mi adlandırıyorlar? İnsan yargısı hâlâ son savunma hattıdır.

## Hangi durumda hangisini seçmeli

| Durum | Seçin |
|-----------|------|
| Kısa metin (tweet'ler, incelemeler, başlıklar) | BERTopic |
| Konu karışımlı uzun belgeler | LDA |
| GPU yok / sınırlı hesaplama | LDA veya NMF |
| Belge düzeyinde çoklu konu dağılımları gerekiyor | LDA |
| Konu etiketleme için LLM entegrasyonu | BERTopic (doğrudan destek) |
| Kaynak kısıtlı uç bilgisayar dağıtımı | LDA |
| Maksimum anlamsal tutarlılık | BERTopic |

En büyük pratik husus belge uzunluğudur. BERT embedding'leri kesilir; LDA sayıları herhangi bir uzunlukta çalışır. Embedding modelinin bağlamından daha uzun belgeler için, ya parçalayıp toplayın ya da LDA kullanın.

## Kullan

2026 stacki:

- **BERTopic.** Kısa metin ve anlamsallığın önemli olduğu her şey için varsayılan.
- **`gensim.models.LdaModel`.** Production için klasik LDA, olgun, savaşta test edilmiş.
- **`sklearn.decomposition.LatentDirichletAllocation`.** Deneyler için kolay LDA.
- **NMF.** Negatif olmayan matris ayrıştırması. LDA için hızlı alternatif, kısa metinde karşılaştırılabilir kalite.
- **Top2Vec.** BERTopic'e benzer tasarım. Daha küçük topluluk ama bazı benchmark'larda iyi.
- **FASTopic.** Daha yeni, çok büyük corpus'larda BERTopic'ten daha hızlı.
- **LLM tabanlı etiketleme.** Herhangi bir kümeleme çalıştırın, sonra her kümeye isim vermesi için bir modele prompt verin.

## Ürün Haline Getir

`outputs/skill-topic-picker.md` olarak kaydedin:

```markdown
---
name: topic-picker
description: Pick LDA or BERTopic for a corpus. Specify library, knobs, evaluation.
version: 1.0.0
phase: 5
lesson: 15
tags: [nlp, topic-modeling]
---

Given a corpus description (document count, avg length, domain, language, compute budget), output:

1. Algorithm. LDA / NMF / BERTopic / Top2Vec / FASTopic. One-sentence reason.
2. Configuration. Number of topics: `recommended = max(5, round(sqrt(n_docs)))`, clamped to 200 for corpora under 40,000 docs; permit >200 only when the corpus is genuinely large (>40k) and note the increased compute cost. `min_df` / `max_df` filters and embedding model for neural approaches also belong here.
3. Evaluation. Topic coherence (c_v) via `gensim.models.CoherenceModel`, topic diversity, and a 20-sample human read.
4. Failure mode to probe. For LDA, "junk topics" absorbing stopwords and frequent terms. For BERTopic, the -1 outlier cluster swallowing ambiguous documents.

Refuse BERTopic on documents longer than the embedding model's context window without a chunking strategy. Refuse LDA on very short text (tweets, reviews under 10 tokens) as coherence collapses. Flag any n_topics choice below 5 as likely wrong; flag >200 on corpora under 40k docs as likely over-splitting.
```

#### Açıklama
Bu, bir corpus açıklaması verildiğinde algoritma, konfigürasyon, değerlendirme ve hata modu seçen bir skill tanımıdır.

## Alıştırmalar

1. **Kolay.** 20 Newsgroups veri seti üzerinde 5 konu ile LDA uyun. Her konu için üst 10 kelimeyi yazdırın. Her konuyu elle etiketleyin. Algoritma gerçek kategorileri buldu mu?
2. **Orta.** Aynı 20 Newsgroups alt kümesi üzerinde BERTopic uyun. Bulunan konu sayısı, üst kelimeler ve nitelenik tutarlılığı LDA ile karşılaştırın. Hangisi gerçek kategorileri daha temiz yüzeye çıkarıyor?
3. **Zor.** Hem LDA hem de BERTopic için corpus'unuz üzerinde c_v tutarlılığı hesaplayın. Her birini 5, 10, 20, 50 konu ile çalıştırın. Tutarlılığı konu sayısına göre çizin. Hangi yöntemin konu sayıları boyunca daha kararlı olduğunu raporlayın.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Konu | Corpus'un hakkında olduğu bir şey | Kelimeler üzerine olasılık dağılımı (LDA) veya benzer belgelerin bir kümesi (BERTopic). |
| Karışık üyelik | Belge birden fazla konu | LDA, her belgeye tüm konular üzerine bir dağılım atar. |
| UMAP | Boyut düşürme | Yerel yapıyı koruyan manifold öğrenme; BERTopic'te kullanılır. |
| HDBSCAN | Yoğunluk kümelemesi | Değişken boyutlu kümeler bulur; aykırılar için "gürültü" etiketi (-1) üretir. |
| c_v tutarlılığı | Konu kalite metriği | Kayan pencereler içinde üst konu kelimelerinin ortalama nokta Mutual Information'ı. |

## İleri Okuma

- [Blei, Ng, Jordan (2003). Latent Dirichlet Allocation](https://www.jmlr.org/papers/volume3/blei03a/blei03a.pdf) — LDA makalesi.
- [Grootendorst (2022). BERTopic: Neural topic modeling with a class-based TF-IDF procedure](https://arxiv.org/abs/2203.05794) — BERTopic makalesi.
- [Röder, Both, Hinneburg (2015). Exploring the Space of Topic Coherence Measures](https://svn.aksw.org/papers/2015/WSDM_Topic_Evaluation/public.pdf) — c_v ve arkadaşlarını tanıtan makale.
- [BERTopic documentation](https://maartengr.github.io/BERTopic/) — production referansı. Mükemmel örnekler.