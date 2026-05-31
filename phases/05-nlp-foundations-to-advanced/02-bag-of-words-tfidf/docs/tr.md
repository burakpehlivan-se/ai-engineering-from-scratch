# Bag of Words, TF-IDF ve Metin Temsili

> Önce say, sonra düşün. TF-IDF, 2026'da iyi tanımlanmış görevlerde hâlâ embedding'leri yener.

**Tür:** İnşa
**Diller:** Python
**Ön Koşullar:** Faz 5 · 01 (Metin İşleme), Faz 2 · 02 (Sıfırdan Doğrusal Regresyon)
**Süre:** ~75 dakika

## Problem

Modelin sayılara ihtiyacı var. Sizin dizgeleriniz var.

Her NLP hattı aynı soruyu yanıtlamalı. Değişken uzunluklu bir token akışını, bir sınıflandırıcının tüketebileceği sabit boyutlu bir vektöre nasıl dönüştürürüz. Alanın ulaştığı ilk cevap, işe yarayan en aptal olanıydı. Kelimeleri say. Bir vektör yap.

O vektör, herhangi bir embedding modelinden daha fazla üretim NLP'si taşımıştır. Spam filtreleri, konu sınıflandırıcıları, log anormallik tespiti, arama sıralaması (BM25'ten önce), sentiment analysis'ın ilk dalgası, akademik NLP benchmark'larının ilk on yılı. 2026 uygulayıcıları hâlâ dar sınıflandırma görevlerinde ilk olarak buna başvurur. Hızlıdır, yorumlanabilirdir ve kelime varlığının önemli olduğu görevlerde 400 milyon parametrelik bir embedding modeliyle sıklıkla ayırt edilemez.

Bu ders bag of words'ü sıfırdan oluşturur, ardından TF-IDF'i. Sonra scikit-learn'ün aynı işi üç satırda nasıl yaptığını gösterir. Ardından sizi embedding'lere yönlendiren başarısızlık modunu adlandırır.

## Kavram

**Bag of Words (BoW)** sırayı atar. Her belge için, her vocabulary (kelime haznesi) kelimesinin kaç kez göründüğünü sayar. Vektör uzunluğu vocabulary boyutudur. `i` pozisyonu `i` kelimesinin sayısıdır.

**TF-IDF** BoW'ı yeniden ağırlıklandırır. Her belgede görünen bir kelime bilgilendirici değildir, bu yüzden küçültün. Corpus (derleme) genelinde nadir ama tek bir belgede sık görünen bir kelime sinyaldir, bu yüzden büyütün.

```
TF-IDF(w, d) = TF(w, d) * IDF(w)
             = count(w in d) / |d| * log(N / df(w))
```

Burada `TF` belgedeki terim sıklığıdır, `df` belge sıklığıdır (kelimeyi kaç belgenin içerdiği), `N` toplam belge sayısıdır. `log`, her yerde görünen kelimeler için ağırlığı sınırlı tutar.

Anahtar özellik: her ikisi de yorumlanabilir eksenlere sahip seyrek vektörler üretir. Eğitilmiş bir sınıflandırıcının ağırlıklarına bakabilir ve hangi kelimelerin bir belgeyi bir sınıfa doğru ittiğini okuyabilirsiniz. Bunu 768 boyutlu bir BERT embedding'i ile yapamazsınız.

## İnşa Et

### Adım 1: vocabulary'yi oluşturma

```python
def build_vocab(docs):
    vocab = {}
    for doc in docs:
        for token in doc:
            if token not in vocab:
                vocab[token] = len(vocab)
    return vocab
```

Girdi: tokenlanmış belgelerin listesi (herhangi bir kelime düzeyi tokenizer işe yarar; bu dersteki `code/main.py` basitleştirilmiş küçük harf varyantı kullanır). Çıktı: `{kelime: indeks}` sözlüğü. Kararlı ekleme sırası, kelime indeksi 0'ın ilk belgede görünen ilk kelime olduğunu anlamına gelir. Sözleşme değişir; scikit-learn alfabetik sıralar.

### Adım 2: bag of words

```python
def bag_of_words(docs, vocab):
    matrix = [[0] * len(vocab) for _ in docs]
    for i, doc in enumerate(docs):
        for token in doc:
            if token in vocab:
                matrix[i][vocab[token]] += 1
    return matrix
```

```python
>>> docs = [["cat", "sat", "on", "mat"], ["cat", "cat", "ran"]]
>>> vocab = build_vocab(docs)
>>> bag_of_words(docs, vocab)
[[1, 1, 1, 1, 0], [2, 0, 0, 0, 1]]
```

Satırlar belgelerdir. Sütunlar vocabulary indeksleridir. `[i][j]` girişi "`j` kelimesi `i` belgesinde kaç kez görünüyor" demektir. Belge 1'de `cat` iki kez var çünkü öyle. Belge 0'da `ran` sıfır kez var çünkü yok.

### Adım 3: terim sıklığı ve belge sıklığı

```python
import math


def term_frequency(doc_bow, doc_length):
    return [c / doc_length if doc_length else 0 for c in doc_bow]


def document_frequency(bow_matrix):
    df = [0] * len(bow_matrix[0])
    for row in bow_matrix:
        for j, count in enumerate(row):
            if count > 0:
                df[j] += 1
    return df


def inverse_document_frequency(df, n_docs):
    return [math.log((n_docs + 1) / (d + 1)) + 1 for d in df]
```

Adlandırmaya değer iki yumuşatma hilesi. `(n+1)/(d+1)` ifadesi `log(x/0)` durumunu önler. Sondaki `+1`, her belgedeki bir kelimenin IDF'inin 1 (0 değil) olmasını sağlar; bu scikit-learn'ün varsayılanıyla eşleşir. Diğer uygulamalar ham `log(N/df)` kullanır. İkisi de çalışır; yumuşatılmış versiyon daha dostane.

### Adım 4: TF-IDF

```python
def tfidf(bow_matrix):
    n_docs = len(bow_matrix)
    df = document_frequency(bow_matrix)
    idf = inverse_document_frequency(df, n_docs)
    out = []
    for row in bow_matrix:
        length = sum(row)
        tf = term_frequency(row, length)
        out.append([tf_j * idf_j for tf_j, idf_j in zip(tf, idf)])
    return out
```

```python
>>> docs = [
...     ["the", "cat", "sat"],
...     ["the", "dog", "sat"],
...     ["the", "cat", "ran"],
... ]
>>> vocab = build_vocab(docs)
>>> bow = bag_of_words(docs, vocab)
>>> tfidf(bow)
```

Üç belge, beş vocabulary kelimesi (`the`, `cat`, `sat`, `dog`, `ran`). `the" üçünde de görünüyor, bu yüzden IDF'i düşük. `dog` birinde görünüyor, bu yüzden IDF'i yüksek. Vektörler seyrek (çoğu giriş küçüktür) ve ayırt edici kelimeler öne çıkar.

### Adım 5: satırları L2-normalize etme

```python
def l2_normalize(matrix):
    out = []
    for row in matrix:
        norm = math.sqrt(sum(x * x for x in row))
        out.append([x / norm if norm else 0 for x in row])
    return out
```

Normalize etmeden, daha uzun bir belge daha büyük bir vektör alır ve benzerlik puanlarına hakim olur. L2 normalizasyonu her belgeyi birim hipersferine koyar. Satırlar arasındaki cosinesimilarity artık sadece bir nokta çarpımıdır.

## Kullan

scikit-learn üretim versiyonunu içerir.

```python
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

docs = ["the cat sat on the mat", "the dog sat on the mat", "the cat ran"]

bow_vectorizer = CountVectorizer()
bow = bow_vectorizer.fit_transform(docs)
print(bow_vectorizer.get_feature_names_out())
print(bow.toarray())

tfidf_vectorizer = TfidfVectorizer()
tfidf = tfidf_vectorizer.fit_transform(docs)
print(tfidf.toarray().round(3))
```

`CountVectorizer` tokenization, vocabulary ve BoW'ı tek bir çağırıda yapar. `TfidfVectorizer` IDF ağırlıklandırmasını ve L2 normalizasyonunu ekler. İkisi de seyrek matrisler döndürür. 100 bin belge için, yoğun versiyon hafızaya sığmaz; sınıflandırıcı yoğun isteyene kadar seyrek kalın.

Her şeyi değiştiren ayarlar:

| Argüman | Etki |
|-----|--------|
| `ngram_range=(1, 2)` | Bigram'ları dahil et. Genellikle sınıflandırmayı artırır. |
| `min_df=2` | 2'den az belgedeki kelimeleri bırak. Gürültülü verilerde vocabulary'yi traşlar. |
| `max_df=0.95` | %95'ten fazla belgedeki kelimeleri bırak. Hazır bir liste olmadan stopwords kaldırmayı yaklaşık olarak yapar. |
| `stop_words="english"` | scikit-learn'ün yerleşik stopwords listesi. Göreve bağlıdır — sentiment analysis olumsuzlukları *kaldırmamalıdır*. |
| `sublinear_tf=True` | Ham `tf` yerine `1 + log(tf)` kullan. Bir terimin tek bir belgede birçok kez tekrarlandığı durumlarda yardımcı olur. |

### TF-IDF'in hâlâ kazandığı durumlar (2026 itibarıyla)

- Spam tespiti, konu etiketleme, log anormalliği işaretleme. Kelime varlığı önemlidir; anlamsal nüans değildir.
- Düşük veri rejimleri (yüzlerce etiketlenmiş örnek). TF-IDF artı lojistik regresyonun önceden eğitim maliyeti yoktur.
- Gecikme süresinin önemli olduğu her yer. TF-IDF artı bir doğrusal model mikrosaniyeler içinde yanıt verir. Bir belgeyi transformer üzerinden embed etmek 10-100 ms alır.
- Tahminlerini açıklaması gereken sistemler. Sınıflandırıcının katsayılarını inceleyin. En üst pozitif kelimeler neden budur.

### TF-IDF'in başarısız olduğu durumlar

Anlamsal körlük başarısızlığı. Şu iki belgeyi düşünün:

- "The movie was not good at all."
- "The movie was excellent."

Biri olumsuz yorum, biri olumlu. TF-IDF örtüşmeleri tam olarak `{the, movie, was}` kümesidir. Bir bag of words sınıflandırıcısı `not` kelimesinin `good` kelimesinin yakınında etiketi tersine çevirdiğini ezberlemek zorundadır. Yeterli veride bunu öğrenebilir, ancak sözdizimini anlayan bir model kadar zarif olamaz.

Diğer başarısızlık: çıkarımda sözlük-dışı (OOV) kelimeler. IMDb yorumları üzerinde eğitilmiş bir BoW modeli, `Zoomer-approved` token'ı eğitimde hiç görünmemişse ne yapacağını bilemez. Subword embedding'leri (ders 04) bunu ele alır. TF-IDF bunu yapamaz.

### Hibrit: TF-IDF ağırlıklı embedding'ler

2026 pragmatik varsayılanı orta veri sınıflandırması için: TF-IDF ağırlıklarını kelime embedding'leri üzerinde attention olarak kullanın.

```python
def tfidf_weighted_embedding(doc, tfidf_scores, embedding_table, dim):
    vec = [0.0] * dim
    total_weight = 0.0
    for token in doc:
        if token not in embedding_table or token not in tfidf_scores:
            continue
        weight = tfidf_scores[token]
        emb = embedding_table[token]
        for i in range(dim):
            vec[i] += weight * emb[i]
        total_weight += weight
    if total_weight == 0:
        return vec
    return [v / total_weight for v in vec]
```

Embedding'lerden anlamsal kapasite, TF-IDF'ten nadir kelime vurgusu elde edersiniz. Sınıflandıcı havuzlanmış vektör üzerinde eğitilir. sentiment analysis, topic ve niyet sınıflandırmasında yaklaşık 50 bin etiketlenmiş örneğe kadar her ikisinden ayrı olarak daha iyi performans gösterir.

## Ürün Haline Getir

`outputs/prompt-vectorization-picker.md` olarak kaydedin:

```markdown
---
name: vectorization-picker
description: Bir metin sınıflandırma görevi verildiğinde BoW, TF-IDF, embedding veya hibrit önerir.
phase: 5
lesson: 02
---

Bir metin vektorizasyon stratejisi öneriyorsunuz. Bir görev tanımı verildiğinde çıktı olarak:

1. Temsil (BoW, TF-IDF, transformer embedding'leri veya hibrit). Bir cümlede nedenini açıklayın.
2. Belirli vektorizasyon yapılandırması. Kütüphaneyi adlandırın. Argümanları alıntılayın (`ngram_range`, `min_df`, `max_df`, `sublinear_tf`, `stop_words`).
3. Üretimden önce test edilecek bir başarısızlık modu.

Kullanıcının 500'den az etiketlenmiş örneği varsa embedding önermeyi reddedin, TF-IDF taban çizgisinde anlamsal başarısızlık kanıtı göstermedikçe. sentiment analysis için stopwords kaldırmayı reddedin (olumsuzluklar sinyal taşır). Sınıf dengesizliğini vektorizasyon değişikliğinden fazlasını gerektiriyor olarak işaretleyin.
```

## Alıştırmalar

1. **Kolay.** L2-normalize edilmiş TF-IDF çıktısı üzerinde `cosine_similarity(doc_vec_a, doc_vec_b)` uygulayın. Aynı belgelerin 1.0 puan aldığını ve kelime haznesi olarak ayrışık belgelerin 0.0 puan aldığını doğrulayın.
2. **Orta.** `bag_of_words`'e `n-gram` desteği ekleyin. `n` parametresi `n`-gram'lar üzerinde sayımlar üretir. `["the", "cat", "sat"]` üzerinde `n=2` kullanıldığında `["the cat", "cat sat"]` için bigram sayımları ürettiğini test edin.
3. **Zor.** GloVe 100d vektörlerini kullanarak yukarıdaki TF-IDF ağırlıklı embedding hibritini oluşturun (bir kez indirin, önbelleğe alın). 20 Newsgroups veri kümesinde saf TF-IDF ve saf ortalama havuzlanmış embedding'lerle sınıflandırma doğruluğunu karşılaştırın. Nerede hangisinin kazandığını raporlayın.

## Anahtar Terimler

| Terim | İnsanların Söylediği | Gerçekte Ne Anlama Gelir |
|------|-----------------|-----------------------|
| BoW | Kelime frekans vektörü | Bir belgedeki vocabulary kelimelerinin sayımları. Sırayı atar. |
| TF | Terim sıklığı | Bir belgedeki bir kelimenin sayısı, isteğe bağlı olarak belge uzunluğuna göre normalize edilmiş. |
| DF | Belge sıklığı | Kelimeyi en az bir kez içeren belge sayısı. |
| IDF | Ters belge sıklığı | Yumuşatılmış `log(N / df)`. Her yerde görünen kelimelerin ağırlığını azaltır. |
| Seyrek vektör | Çoğunlukla sıfırlar | Vocabulary genellikle 10k-100k kelime; herhangi bir belgede çoğu bulunmaz. |
| Cosinesimilarity | Vektör açısı | L2-normalize edilmiş vektörlerin nokta çarpımı. 1 özdeştir, 0 dik açılıdır. |

## İleri Okuma

- [scikit-learn — feature extraction from text](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction) — kanonik API referansı, artı her ayar hakkında notlar.
- [Salton, G., & Buckley, C. (1988). Term-weighting approaches in automatic text retrieval](https://www.sciencedirect.com/science/article/pii/0306457388900210) — TF-IDF'i bir on yıl boyunca varsayılan yapan makale.
- ["Why TF-IDF Still Beats Embeddings" — Ashfaque Thonikkadavan (Medium)](https://medium.com/@cmtwskb/why-tf-idf-still-beats-embeddings-ad85c123e1b2) — 2026'da eski yöntemin neden kazandığına dair bakış.
