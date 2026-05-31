# GloVe, FastText ve Subword Embedding'leri

> Word2Vec kelime başına bir embedding eğitti. GloVe eş-zamanlı olma matrisini faktörize etti. FastText parçaları embed etti. BPE'yi transformer'lara köprü yaptı.

**Tür:** İnşa
**Diller:** Python
**Ön Koşullar:** Faz 5 · 03 (Word2Vec'i Sıfırdan)
**Süre:** ~45 dakika

## Problem

Word2Vec iki açık soru bıraktı.

Birincisi, eş-zamanlı olma matrisini doğrudan faktörize eden (LSA, HAL) paralel bir araştırma çizgisi vardı; çevrimiçi skip-gram güncellemeleri yapmak yerine. Word2Vec'in yinelemeli yaklaşımı temelde daha mı iyiydi, yoksa fark iki yöntemin sayımları nasıl ele aldığından mı kaynaklanıyordu? **GloVe** buna cevap verdi: dikkatlice seçilmiş bir kayıpla matris faktörizasyonu Word2Vec'e eşit veya daha iyidir ve eğitim maliyeti daha düşüktür.

İkincisi, hiçbir yöntem daha önce hiç görmediği kelimeler için bir hikaye değildi. `Zoomer-approved`, `dogecoin`, geçen hafta türetilmiş her özel isim, nadir bir kökün çekimli her formu. **FastText** bunu karakter n-gram'larını embed ederek çözdü: bir kelime, morfemler de dahil olmak üzere parçalarının toplamıdır; bu yüzden sözlük-dışı kelimeler bile makul bir vektör alır.

Üçüncüsü, transformer'lar geldiğinde soru tekrar değişti. Kelime düzeyi vocabulary'leri yaklaşık bir milyon girişle sınırlıdır; gerçek dil bundan daha açıktır. **Byte-pair encoding (BPE)** ve akrabaları, her şeyi kapsayan sık subword birimlerinden oluşan bir vocabulary öğrenerek bunu çözdü. Her modern LLM için her modern tokenizer bir subword tokenizer'ıdır.

Bu ders üçünü ele alır ve ardından hangisine ne zaman başvurulacağını açıklar.

## Kavram

**GloVe (Global Vectors).** Kelime-kelime eş-zamanlı olma matrisi `X`'i oluşturun; burada `X[i][j]` `j` kelimesinin `i` kelimesinin bağlamında kaç kez göründüğüdür. `v_i · v_j + b_i + b_j ≈ log(X[i][j])` olacak şekilde vektörler eğitin. Sık çiftlerin hakim olmaması için kaybı ağırlıklandırın. Bitti.

**FastText.** Bir kelime, karakter n-gram'larının toplamıdır artı kelimenin kendisi. `where` kelimesi `<wh, whe, her, ere, re>, <where>` olur. Kelime vektörü bu bileşen vektörlerin toplamıdır. Word2Vec gibi eğitilir. Fayda: görünmeyen kelimeler (`whereupon`) bilinen n-gram'lardan bileşir.

**BPE (Byte-Pair Encoding).** Tek baytlardan (veya karakterlerden) oluşan bir vocabulary ile başlayın. Corpus'taki her bitişik çifti sayın. En sık çifti yeni bir token olarak birleştirin. `k` yineleme için tekrarlayın. Sonuç: `k + 256` token'dan oluşan bir vocabulary; sık diziler (`ing`, `tion`, `the`) tek token olur ve nadir kelimeler tanıdık parçalara bölünür. Her cümle bilinen bir şeye tokenize edilir.

## İnşa Et

### GloVe: eş-zamanlı olma matrisini faktörize etme

```python
import numpy as np
from collections import Counter


def build_cooccurrence(docs, window=5):
    pair_counts = Counter()
    vocab = {}
    for doc in docs:
        for token in doc:
            if token not in vocab:
                vocab[token] = len(vocab)
    for doc in docs:
        indexed = [vocab[t] for t in doc]
        for i, center in enumerate(indexed):
            for j in range(max(0, i - window), min(len(indexed), i + window + 1)):
                if i != j:
                    distance = abs(i - j)
                    pair_counts[(center, indexed[j])] += 1.0 / distance
    return vocab, pair_counts


def glove_train(vocab, pair_counts, dim=16, epochs=100, lr=0.05, x_max=100, alpha=0.75, seed=0):
    n = len(vocab)
    rng = np.random.default_rng(seed)
    W = rng.normal(0, 0.1, size=(n, dim))
    W_tilde = rng.normal(0, 0.1, size=(n, dim))
    b = np.zeros(n)
    b_tilde = np.zeros(n)

    for epoch in range(epochs):
        for (i, j), x_ij in pair_counts.items():
            weight = (x_ij / x_max) ** alpha if x_ij < x_max else 1.0
            diff = W[i] @ W_tilde[j] + b[i] + b_tilde[j] - np.log(x_ij)
            coef = weight * diff

            grad_W_i = coef * W_tilde[j]
            grad_W_tilde_j = coef * W[i]
            W[i] -= lr * grad_W_i
            W_tilde[j] -= lr * grad_W_tilde_j
            b[i] -= lr * coef
            b_tilde[j] -= lr * coef

    return W + W_tilde
```

Adlandırmaya değer iki hareketli parça. Ağırlıklandırma işlevi `f(x) = (x/x_max)^alpha` çok sık çiftlerin (örneğin `(the, and)`) ağırlığını azaltır; böylece kayba hakim olmazlar. Son embedding, `W` (merkez) ve `W_tilde` (bağlam) tablolarının toplamıdır. Her ikisini toplamak, genellikle birini kullanmaktan daha iyi performans gösteren yayınlanmış bir numaradır.

### FastText: subword farkında embedding'ler

```python
def char_ngrams(word, n_min=3, n_max=6):
    wrapped = f"<{word}>"
    grams = {wrapped}
    for n in range(n_min, n_max + 1):
        for i in range(len(wrapped) - n + 1):
            grams.add(wrapped[i:i + n])
    return grams
```

```python
>>> char_ngrams("where")
{'<where>', '<wh', 'whe', 'her', 'ere', 're>', '<whe', 'wher', 'here', 'ere>', '<wher', 'where', 'here>'}
```

Her kelime, n-gram kümesi (genellikle 3 ila 6 karakter) ile temsil edilir. Kelime embedding'i, n-gram embedding'lerinin toplamıdır. Skip-gram eğitimi için, Word2Vec'in tek bir vektör kullandığı yere bunu yerleştirin.

```python
def fasttext_vector(word, ngram_table):
    grams = char_ngrams(word)
    vecs = [ngram_table[g] for g in grams if g in ngram_table]
    if not vecs:
        return None
    return np.sum(vecs, axis=0)
```

Görülmemiş bir kelime için, bazı n-gram'ları biliniyorsa hâlâ bir vektör alırsınız. `whereupon`, `where` ile `<wh`, `her`, `ere` ve `<where` paylaştığı için ikisi birbirine yakın değerler alır.

### BPE: öğrenilmiş subword vocabulary

```python
def learn_bpe(corpus, k_merges):
    vocab = Counter()
    for word, freq in corpus.items():
        tokens = tuple(word) + ("</w>",)
        vocab[tokens] = freq

    merges = []
    for _ in range(k_merges):
        pair_freq = Counter()
        for tokens, freq in vocab.items():
            for a, b in zip(tokens, tokens[1:]):
                pair_freq[(a, b)] += freq
        if not pair_freq:
            break
        best = pair_freq.most_common(1)[0][0]
        merges.append(best)

        new_vocab = Counter()
        for tokens, freq in vocab.items():
            new_tokens = []
            i = 0
            while i < len(tokens):
                if i + 1 < len(tokens) and (tokens[i], tokens[i + 1]) == best:
                    new_tokens.append(tokens[i] + tokens[i + 1])
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1
            new_vocab[tuple(new_tokens)] = freq
        vocab = new_vocab
    return merges


def apply_bpe(word, merges):
    tokens = list(word) + ["</w>"]
    for a, b in merges:
        new_tokens = []
        i = 0
        while i < len(tokens):
            if i + 1 < len(tokens) and tokens[i] == a and tokens[i + 1] == b:
                new_tokens.append(a + b)
                i += 2
            else:
                new_tokens.append(tokens[i])
                i += 1
        tokens = new_tokens
    return tokens
```

```python
>>> corpus = Counter({"low": 5, "lower": 2, "newest": 6, "widest": 3})
>>> merges = learn_bpe(corpus, k_merges=10)
>>> apply_bpe("lowest", merges)
['low', 'est</w>']
```

İlk yineleme en sık bitişik çifti birleştirir. Yeterli yinelemeden sonra sık alt diziler (`low`, `est`, `tion`) tek token haline gelir ve nadir kelimeler temiz bir şekilde bölünür.

Gerçek GPT / BERT / T5 tokenizer'ları 30 bin-100 bin birleştirme öğrenir. Sonuç: herhangi bir metin bilinen ID'lerin sınırlı uzunluklu bir dizisine tokenize edilir; asla OOV olmaz.

## Kullan

Pratikte, bunların hiçbirini nadiren kendiniz eğitirsiniz. Önceden eğitilmiş kontrol noktalarını yüklersiniz.

```python
import fasttext.util
fasttext.util.download_model("en", if_exists="ignore")
ft = fasttext.load_model("cc.en.300.bin")
print(ft.get_word_vector("whereupon").shape)
print(ft.get_word_vector("zoomerapproved").shape)
```

Transformer çağında BPE tarzı subword tokenizasyonu için:

```python
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("gpt2")
print(tok.tokenize("unbelievably tokenized"))
```

```
['un', 'bel', 'iev', 'ably', 'Ġtoken', 'ized']
```

`Ġ` öneki kelime sınırlarını işaretler (GPT-2 sözleşmesi). Her modern tokenizer bir BPE varyantı, WordPiece (BERT) veya SentencePiece (T5, LLaMA)'dır.

### Hangisini ne zaman seçmeli

| Durum | Seçin |
|-----------|------|
| Önceden eğitilmiş genel amaçlı kelime vektörleri, OOV toleransı gerekmez | GloVe 300d |
| Önceden eğitilmiş genel amaçlı kelime vektörleri, yazım hataları / yeni türemeler / morfolojik olarak zengin diller ele alınmalı | FastText |
| Transformer'a giren her şey (eğitim veya çıkarım) | Modelin geldiği herhangi bir tokenizer. Asla değiştirmeyin. |
| Sıfırdan kendi dil modelinizi eğitmek | Önce corpus'unuz üzerinde bir BPE veya SentencePiece tokenizer eğitin |
| Doğrusal modelle üretim metin sınıflandırması | Hâlâ TF-IDF. Ders 02. |

## Ürün Haline Getir

`outputs/skill-embeddings-picker.md` olarak kaydedin:

```markdown
---
name: tokenizer-picker
description: Yeni bir dil modeli veya metin hattı için bir tokenization yaklaşımı seçin.
version: 1.0.0
phase: 5
lesson: 04
tags: [nlp, tokenization, embeddings]
---

Bir görev ve veri kümesi tanımı verildiğinde çıktı olarak:

1. Tokenization stratejisi (kelime düzeyi, BPE, WordPiece, SentencePiece, bayt düzeyi). Bir cümlelik neden.
2. Vocabulary boyutu hedefi (örneğin, yalnızca İngilizce bir dil modeli için 32k, çok dilli için 64k-100k).
3. Tam eğitim komutuyla kütüphane çağrısı. Kütüphaneyi adlandırın. Argümanları alıntılayın.
4. Bir tekrar üretilebilirlik tuzağı. Tokenizer-model uyumsuzluğu en yaygın sessiz üretim hatasıdır; hangi çiftin birlikte kullanılması gerektiğini belirtin.

Kullanıcı önceden eğitilmiş bir LLM'de fine-tuning yapıyorsa özel bir tokenizer eğitmeyi önermeyi reddedin. Üretim çıkarımını hedefleyen herhangi bir model için kelime düzeyi tokenizasyon önermeyi reddedin. İngilizce olmayan / çok yazılımlı corpus'ları byte fallback ile SentencePiece gerektiriyor olarak işaretleyin.
```

## Alıştırmalar

1. **Kolay.** `char_ngrams("playing")` ve `char_ngrams("played")`'ı çalıştırın. İki n-gram kümesinin Jaccard örtüşmesini hesaplayın. Önemli ortak parçalar görmelisiniz (`pla`, `lay`, `play`); bu yüzden FastText morfolojik varyantlar arasında iyi transfer olur.
2. **Orta.** `learn_bpe`'yi vocabulary büyümesini izleyecek şekilde genişletin. Token sayısını corpus karakterine göre birleştirme sayısının işlevi olarak çizin. İlk başta hızlı sıkıştırma, token başına yaklaşık 2-3 karaktere doğru asimptotikleşme görmelisiniz.
3. **Zor.** Shakespeare'in tüm eserleri üzerinde 1000 birleştirmeli bir BPE eğitin. Sık kelimelerin tokenizasyonunu nadir özel isimlerle karşılaştırın. Öncesi ve sonrası kelime başına ortalama token sayısını ölçün. Sizi şaşırtan şeyleri yazın.

## Anahtar Terimler

| Terim | İnsanların Söylediği | Gerçekte Ne Anlama Gelir |
|------|-----------------|-----------------------|
| Eş-zamanlı olma matrisi | Kelime-kelime frekans tablosu | `X[i][j]` = `j` kelimesinin `i` kelimesi çevresindeki bir pencerede kaç kez göründüğü. |
| Subword | Bir kelimenin parçası | Bir karakter n-gram'ı (FastText) veya öğrenilmiş token (BPE/WordPiece/SentencePiece). |
| BPE | Byte-pair encoding | Vocabulary hedef boyutuna ulaşana kadar en sık bitişik çiftlerin yinelemeli birleştirilmesi. |
| OOV | Sözlük dışı | Modelin hiç görmediği kelime. Word2Vec/GloVe başarısız olur. FastText ve BPE ele alır. |
| Bayt düzeyi BPE | Ham baytlar üzerinde BPE | GPT-2'nin şeması. Vocabulary 256 baytla başlar; hiçbir şey asla OOV olmaz. |

## İleri Okuma

- [Pennington, Socher, Manning (2014). GloVe: Global Vectors for Word Representation](https://nlp.stanford.edu/pubs/glove.pdf) — GloVe makalesi, yedi sayfa, kaybın hâlâ en iyi türetmesi.
- [Bojanowski et al. (2017). Enriching Word Vectors with Subword Information](https://arxiv.org/abs/1607.04606) — FastText.
- [Sennrich, Haddow, Birch (2016). Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/abs/1508.07909) — BPE'yi modern NLP'ye tanıtan makale.
- [Hugging Face tokenizer summary](https://huggingface.co/docs/transformers/tokenizer_summary) — BPE, WordPiece ve SentencePiece pratikte nasıl farklıdır.
