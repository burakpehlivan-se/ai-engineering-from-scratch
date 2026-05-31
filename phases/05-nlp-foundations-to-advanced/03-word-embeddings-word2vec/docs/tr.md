# Word Embedding'ler — Word2Vec'i Sıfırdan

> Bir kelime, kendisini çevreleyenlerle anılır. Bu fikir üzerinde sığ bir sinir ağı eğitin, geometri ortaya çıkar.

**Tür:** İnşa
**Diller:** Python
**Ön Koşullar:** Faz 5 · 02 (BoW + TF-IDF), Faz 3 · 03 (Sıfırdan Backpropagation)
**Süre:** ~75 dakika

## Problem

TF-IDF `dog` ve `puppy` kelimelerinin farklı kelimeler olduğunu bilir. Neredeyse aynı anlama geldiklerini bilmez. `dog` üzerinde eğitilmiş bir sınıflandırıcı `puppy` üzerine yazılmış bir yorumu genelleştiremez. Eş anlamlıları listeleyerek bunu örtbas edebilirsiniz, ancak bu nadir terimlerde, alan jargonunda ve öngörmediğiniz her dilde başarısız olur.

`dog` ve `puppy`'nin uzayda birbirine yakın olmasını istediğiniz bir temsil istiyorsunuz. `king - man + woman`'ın `queen`'e yakın landing yaptığı bir temsil. `dog` üzerinde eğitilmiş bir modelin `puppy`'ye ücretsiz olarak sinyal aktardığı bir temsil.

Word2Vec bize bu uzayı verdi. İki katmanlı sinir ağı, trilyon token eğitim çalışması, 2013'te yayınlandı. Mimari neredeyse utanç verici kadar basit. Sonuçlar on yıl boyunca NLP'yi yeniden şekillendirdi.

## Kavram

**Dağıtsal hipotez** (Firth, 1957): "Bir kelimeyi, kendisini çevreleyenlerle tanıyacaksınız." İki kelime benzer bağlamda görünüyorsa, muhtemelen benzer anlamlar gelirir.

Word2Vec iki versiyonda gelir; ikisi de bu fikri istismar eder.

- **Skip-gram.** Merkez kelime verildiğinde, çevresindeki kelimeleri tahmin et. Pencere boyutu 2 ile `cat -> (the, sat, on)`.
- **CBOW (continuous bag of words).** Çevresindeki kelimeler verildiğinde, merkezi tahmin et. `(the, sat, on) -> cat`.

Skip-gram eğitimi daha yavaştır ama nadir kelimeleri daha iyi ele alır. Varsayılan haline geldi.

Ağda doğrusallık olmayan bir gizli katman vardır. Girdi, vocabulary üzerinde bir one-hot vektörüdür. Çıktı, vocabulary üzerinde bir softmax'tır. Eğitimden sonra çıkış katmanını atarsınız. Gizli katman ağırlıkları embedding'lerdir.

```
one-hot(center) ── W ──▶ hidden (d-dim) ── W' ──▶ softmax(vocab)
                          ^
                          bu embedding'dir
```

Numara: 100 bin kelime üzerinde softmax aşırı pahalıdır. Word2Vec, bunu bir ikili sınıflandırma görevine dönüştürmek için **negative sampling** kullanır. "Bu bağlam kelimesi bu merkez kelimesinin yakınında göründü mü, evet mi hayır mı" tahmin edin. Eğitim çifti başına birkaç olumsuz (eş-zamanlı görünmeyen) kelime örnekleme yapın; tüm vocabulary üzerinde softmax hesaplamak yerine.

## İnşa Et

### Adım 1: corpus'tan eğitim çiftleri

```python
def skipgram_pairs(docs, window=2):
    pairs = []
    for doc in docs:
        for i, center in enumerate(doc):
            for j in range(max(0, i - window), min(len(doc), i + window + 1)):
                if i == j:
                    continue
                pairs.append((center, doc[j]))
    return pairs
```

```python
>>> skipgram_pairs([["the", "cat", "sat", "on", "mat"]], window=2)
[('the', 'cat'), ('the', 'sat'),
 ('cat', 'the'), ('cat', 'sat'), ('cat', 'on'),
 ('sat', 'the'), ('sat', 'cat'), ('sat', 'on'), ('sat', 'mat'),
 ...]
```

Penceredeki her (merkez, bağlam) çifti pozitif bir eğitim örneğidir.

### Adım 2: embedding tabloları

İki matris. `W` merkez kelime embedding tablosudur (sakladığınız). `W'` bağlam kelimesi tablosudur (genellikle atılır, bazen `W` ile ortalama yapılır).

```python
import numpy as np


def init_embeddings(vocab_size, dim, seed=0):
    rng = np.random.default_rng(seed)
    W = rng.normal(0, 0.1, size=(vocab_size, dim))
    W_prime = rng.normal(0, 0.1, size=(vocab_size, dim))
    return W, W_prime
```

Küçük rastgele başlatma. Vocabulary boyutu 10 bin ve boyut 100 gerçektir; öğretim için, 50 vocabulary x 16 boyut geometriyi görmek için yeterlidir.

### Adım 3: negative sampling hedefi

Her pozitif çift `(merkez, bağlam)` için, vocabulary'den `k` rastgele kelime olumsuz olarak örnekle. Modeli, pozitifler için nokta çarpımı `W[merkez] · W'[bağlam]` yüksek, olumsuzlar için düşük olacak şekilde eğit.

```python
def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -20, 20)))


def train_pair(W, W_prime, center_idx, context_idx, negative_indices, lr):
    v_c = W[center_idx]
    u_pos = W_prime[context_idx]
    u_negs = W_prime[negative_indices]

    pos_score = sigmoid(v_c @ u_pos)
    neg_scores = sigmoid(u_negs @ v_c)

    grad_center = (pos_score - 1) * u_pos
    for i, u in enumerate(u_negs):
        grad_center += neg_scores[i] * u

    W[context_idx] = W[context_idx]
    W_prime[context_idx] -= lr * (pos_score - 1) * v_c
    for i, neg_idx in enumerate(negative_indices):
        W_prime[neg_idx] -= lr * neg_scores[i] * v_c
    W[center_idx] -= lr * grad_center
```

Sihirli formül: pozitif çift üzerinde lojistik kayıp (sigmoid'i 1'e yakın olmasını istiyoruz) artı olumsuz çiftler üzerinde lojistik kayıp (sigmoid'i 0'a yakın olmasını istiyoruz). Gradyanlar her iki tabloya akar. Tam türetme orijinal makalededir; bir kez kalem ve kağıtla üzerinden yürüyün, yerleşmesi için.

### Adım 4: oyuncak corpus üzerinde eğitim

```python
def train(docs, dim=16, window=2, k_neg=5, epochs=100, lr=0.05, seed=0):
    vocab = build_vocab(docs)
    vocab_size = len(vocab)
    rng = np.random.default_rng(seed)
    W, W_prime = init_embeddings(vocab_size, dim, seed=seed)
    pairs = skipgram_pairs(docs, window=window)

    for epoch in range(epochs):
        rng.shuffle(pairs)
        for center, context in pairs:
            c_idx = vocab[center]
            ctx_idx = vocab[context]
            negs = rng.integers(0, vocab_size, size=k_neg)
            negs = [n for n in negs if n != ctx_idx and n != c_idx]
            train_pair(W, W_prime, c_idx, ctx_idx, negs, lr)
    return vocab, W
```

Büyük bir corpus üzerinde yeterli epoch'tan sonra, bağlamı paylaşan kelimeler benzer merkez embedding'lerine sahip olur. Oyuncak bir corpus üzerinde etkiyi hafifçe görürsünüz. Trilyon token üzerinde dramatik bir şekilde görürsünüz.

### Adım 5: analoji numarası

```python
def nearest(vocab, W, target_vec, topk=5, exclude=None):
    exclude = exclude or set()
    inv_vocab = {i: w for w, i in vocab.items()}
    norms = np.linalg.norm(W, axis=1, keepdims=True) + 1e-9
    W_norm = W / norms
    target = target_vec / (np.linalg.norm(target_vec) + 1e-9)
    sims = W_norm @ target
    order = np.argsort(-sims)
    out = []
    for i in order:
        if i in exclude:
            continue
        out.append((inv_vocab[i], float(sims[i])))
        if len(out) == topk:
            break
    return out


def analogy(vocab, W, a, b, c, topk=5):
    v = W[vocab[b]] - W[vocab[a]] + W[vocab[c]]
    return nearest(vocab, W, v, topk=topk, exclude={vocab[a], vocab[b], vocab[c]})
```

Önceden eğitilmiş 300 boyutlu Google News vektörlerinde:

```python
>>> analogy(vocab, W, "man", "king", "woman")
[('queen', 0.71), ('monarch', 0.62), ('princess', 0.59), ...]
```

`king - man + woman =queen`. Modelin ne olduğunu bildiği için değil. `(king - man)` vektörünün "royal" gibi bir şeyi yakaladığı ve bunu `woman`'a eklemenin kraliyet-dişi bölgesine yakın landing yaptığı için.

## Kullan

Word2Vec'i sıfırdan yazmak öğretim içindir. Üretim NLP'si `gensim` kullanır.

```python
from gensim.models import Word2Vec

sentences = [
    ["the", "cat", "sat", "on", "the", "mat"],
    ["the", "dog", "ran", "across", "the", "room"],
]

model = Word2Vec(
    sentences,
    vector_size=100,
    window=5,
    min_count=1,
    sg=1,
    negative=5,
    workers=4,
    epochs=30,
)

print(model.wv["cat"])
print(model.wv.most_similar("cat", topn=3))
```

Gerçek iş için, neredeyse hiç Word2Vec'i kendiniz eğitmeyiz. Önceden eğitilmiş vektörler indirirsiniz.

- **GloVe** — Stanford'un eş-zamanlı olma matrisi faktörizasyonu yaklaşımı. 50d, 100d, 200d, 300d kontrol noktaları. İyi genel kapsama. Ders 04 GloVe'i özel olarak ele alır.
- **fastText** — Facebook'un karakter n-gram'larını embed eden Word2Vec uzantısı. Subword'leri birleştirerek sözlük-dışı kelimeleri ele alır. Ders 04.
- **Önceden eğitilmiş Word2Vec Google News üzerinde** — 300d, 3 milyon kelime vocabulary'si, 2013'te yayınlandı. Hâlâ her gün indiriliyor.

### Word2Vec'in 2026'da hâlâ kazandığı durumlar

- Hafif ağırlık alan-spesifik geri alma. Tıbbi özetler üzerinde bir saat içinde bir dizüstü bilgisayarda eğitin, hiçbir genel modelin yakalayamayacağı uzmanlaşmış vektörler elde edin.
- Analoji stilinde özellik mühendisliği. `cinsiyet_vektörü = mean(kadın - erkek çiftleri)`. Diğer kelimelerden çıkararak cinsiyet-nö ekseni elde edin. Adalet araştırmasında hâlâ kullanılıyor.
- Yorumlanabilirlik. 100 boyutlu, PCA veya t-SNE ile çizilebilecek kadar küçüktür ve kümelerin oluşumunu gerçekten görebilirsiniz.
- Çıkarımın GPU olmadan cihaz üzerinde çalışması gereken her yer. Word2Vec araması tek bir satır çekme işlemidir.

### Word2Vec'in başarısız olduğu yerler

Polisemi duvarı. `bank`'ın bir vektörü vardır. `river bank` ve `financial bank` bunu paylaşır. `tablo` (elektronik tablo vs mobilya) paylaşır. Aşağı akıştaki bir sınıflandırıcı vektörden anlamları ayırt edemez.

Bağlamsal embedding'ler (ELMo, BERT, o zamandan beri her transformer), her kelimenin appearance'ını çevresine göre farklı bir vektör üreterek bunu çözdü. Word2Vec'ten BERT'e geçiş budur: statikten bağlamsala. Faz 7 transformer bölümünü ele alır.

Sözlük-dışı problem diğer başarısızlıktır. Word2Vec, eğitim verilerinde yoksa `Zoomer-approved` kelimesini hiç görmemiştir. Yedek mekanizma yoktur. fastText bunu subword bileşimiyle (ders 04) çözer.

## Ürün Haline Getir

`outputs/skill-embedding-probe.md` olarak kaydedin:

```markdown
---
name: embedding-probe
description: Bir word2vec modelini inceleyin. Analojileri çalıştırın, komşuları bulun, kaliteyi teşhis edin.
version: 1.0.0
phase: 5
lesson: 03
tags: [nlp, embeddings, debugging]
---

Eğitilmiş word embedding'lerinin çalıştığını doğrulamak için bunları inceliyorsunuz. Bir `gensim.models.KeyedVectors` nesnesi ve bir vocabulary verildiğinde şunları çalıştırıyorsunuz:

1. Üç kanonik analoji testi. `king : man :: queen : woman`. `paris : france :: tokyo : japan`. `walking : walked :: swimming : ?`. İlk-1 sonucunu ve cosinesimilarity'ni raporlayın.
2. Kullanıcının sağladığı alan-spesifik kelimeler üzerinde beş en-yakın-komşu testi. İlk-5 komşuyu cosinesimilarity ile yazdırın.
3. Bir simetri kontrolü. `similarity(a, b) == similarity(b, a)` float hassasiyeti dahilinde.
4. Bir dejenerasyon kontrolü. Herhangi bir embedding normu 0.01'in altında veya 100'ün üzerindeyse, modelde eğitim hatası vardır. İşaretleyin.

Modeli yalnızca analoji doğruluğuna göre iyi ilan etmeyi reddedin. Analoji benchmark'ları manipüle edilebilir ve aşağı akış görevlerine transfer olmaz. Dahili + aşağı akış değerlendirmesini birlikte önerin.
```

## Alıştırmalar

1. **Kolay.** Eğitim döngüsünü küçük bir corpus üzerinde çalıştırın (kediler ve köpekler hakkında 20 cümle). 200 epoch'tan sonra, `nearest(vocab, W, W[vocab["cat"]])` ifadesinin ilk 3'te `dog` döndürdüğünü doğrulayın. Olmazsa, epoch'ları veya vocabulary'yi artırın.
2. **Orta.** Sık kelimelerin alt-örnekleme desteğini ekleyin. `10^-5` üzerinde sıklığa sahip kelimeler, sıklıklarıyla orantılı olasılıkla eğitim çiftlerinden düşürülür. Nadir kelime benzerliği üzerindeki etkiyi ölçün.
3. **Zor.** 20 Newsgroups corpus'u üzerinde bir model eğitin. İki önyargı ekseni hesaplayın: `he - she` ve `doctor - nurse`. Meslek kelimelerini her iki eksene de projekte edin. En büyük önyargı boşluğuna sahip meslekleri raporlayın. Bu, adalet araştırmacılarının kullandığı türden bir problama.

## Anahtar Terimler

| Terim | İnsanların Söylediği | Gerçekte Ne Anlama Gelir |
|------|-----------------|-----------------------|
| Word embedding | Kelime olarak bir vektör | Bağlamdan öğrenilmiş yoğun, düşük boyutlu (genellikle 100-300) temsil. |
| Skip-gram | Word2Vec hilesi | Merkez kelimeyi verip bağlam kelimelerini tahmin et. CBOW'dan daha yavaş, nadir kelimeler için daha iyi. |
| Negative sampling | Eğitim kısayolu | Tam vocabulary üzerinde softmax'i, `k` rastgele kelimeye karşı ikili sınıflandırma ile değiştirin. |
| Statik embedding | Kelime başına bir vektör | Bağlamdan bağımsız olarak aynı vektör. Polisemi'de başarısız olur. |
| Bağlamsal embedding | Bağlama duyarlı vektör | Çevresindeki kelimelere göre her appearance için farklı vektör. Transformer'ların ürettiği. |
| OOV | Sözlük dışı | Eğitimde hiç görülmemiş kelime. Word2Vec bunlar için vektör üretemez. |

## İleri Okuma

- [Mikolov et al. (2013). Distributed Representations of Words and Phrases and their Compositionality](https://arxiv.org/abs/1310.4546) — negative sampling makalesi. Kısa ve okunabilir.
- [Rong, X. (2014). word2vec Parameter Learning Explained](https://arxiv.org/abs/1411.2738) — orijinal makalenin matematikleri yoğun geldiğinde, gradyanların en açık türetmesi.
- [gensim Word2Vec tutorial](https://radimrehurek.com/gensim/models/word2vec.html) — gerçekten çalışan üretim eğitim ayarları.
